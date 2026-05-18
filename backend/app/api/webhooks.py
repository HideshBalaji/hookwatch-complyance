from fastapi import APIRouter, HTTPException, Body, UploadFile, File
import pandas as pd
import io
from typing import List
from app.database.db import SessionLocal
from app.models.webhook import WebhookEvent, Endpoint, DeliveryAttempt, ReplayAction
from app.schemas.intelligence import RawWebhookLogRequest
import uuid

router = APIRouter()

@router.get("/{event_id}")
def get_webhook(event_id: str):
    db = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Webhook not found")
            
        return {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "created_at": event.created_at,
            "attempts": [
                {
                    "attempt_number": a.attempt_number,
                    "http_status": a.http_status,
                    "response_time_ms": a.response_time_ms,
                    "timeout": a.timeout
                } for a in event.attempts
            ]
        }
    finally:
        db.close()

@router.post("/upload")
def upload_webhook_log(user_id: str, payload: RawWebhookLogRequest = Body(...)):
    """
    Uploads a raw webhook operational log (containing endpoint configs, attempts, and replay history)
    and securely stores it into the PostgreSQL database mapped to the specific user_id.
    """
    db = SessionLocal()
    try:
        # 1. Upsert Endpoint Data
        endpoint = db.query(Endpoint).filter(Endpoint.endpoint_id == payload.endpoint.endpoint_id).first()
        if not endpoint:
            endpoint = Endpoint(
                endpoint_id=payload.endpoint.endpoint_id,
                customer_id=payload.customer_id,
                endpoint_url_type="custom",
                expected_signature_version="v1",
                avg_success_rate=payload.endpoint.avg_success_rate,
                rate_limit_per_minute=payload.endpoint.rate_limit_per_minute,
                active=payload.endpoint.active,
                user_id=user_id
            )
            db.add(endpoint)
        else:
            endpoint.avg_success_rate = payload.endpoint.avg_success_rate
            endpoint.rate_limit_per_minute = payload.endpoint.rate_limit_per_minute
            endpoint.active = payload.endpoint.active
            endpoint.user_id = user_id
            
        # 2. Upsert Webhook Event Data
        event = db.query(WebhookEvent).filter(WebhookEvent.event_id == payload.event_id).first()
        if not event:
            event = WebhookEvent(
                event_id=payload.event_id,
                event_type=payload.event_type,
                customer_id=payload.customer_id,
                payload_size_kb=250.0, # Assumed default for live uploads
                idempotency_key=f"idem_{uuid.uuid4().hex[:8]}",
                priority="medium",
                user_id=user_id
            )
            db.add(event)
            
        db.commit() # Flush so attempts can safely reference event_id and endpoint_id
        
        # 3. Store Delivery Attempts
        for attempt in payload.delivery_attempts:
            existing_attempt = db.query(DeliveryAttempt).filter(
                DeliveryAttempt.event_id == payload.event_id,
                DeliveryAttempt.attempt_number == attempt.attempt_number
            ).first()
            
            if not existing_attempt:
                new_attempt = DeliveryAttempt(
                    attempt_id=f"att_{uuid.uuid4().hex[:8]}",
                    event_id=payload.event_id,
                    endpoint_id=payload.endpoint.endpoint_id,
                    attempt_number=attempt.attempt_number,
                    http_status=attempt.http_status,
                    response_time_ms=attempt.response_time_ms,
                    timeout=attempt.timeout,
                    signature_valid=attempt.signature_valid,
                    user_id=user_id
                )
                db.add(new_attempt)
                
        # 4. Store Replay History
        if payload.replay_history and payload.replay_history.previous_replays > 0:
            for i in range(payload.replay_history.previous_replays):
                new_replay = ReplayAction(
                    replay_id=f"rep_{uuid.uuid4().hex[:8]}",
                    event_id=payload.event_id,
                    replay_result="failed" if payload.delivery_attempts[-1].http_status >= 400 else "success",
                    duplicate_detected=payload.replay_history.duplicate_detected,
                    manually_triggered=payload.replay_history.manually_triggered,
                    user_id=user_id
                )
                db.add(new_replay)

        db.commit()
        return {
            "status": "success", 
            "message": "Webhook log uploaded and stored successfully", 
            "event_id": payload.event_id,
            "user_id": user_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database upload failed: {str(e)}")
    finally:
        db.close()


@router.post("/upload/bulk")
def upload_webhook_logs_bulk(user_id: str, payloads: List[RawWebhookLogRequest] = Body(...)):
    """
    Uploads an array of raw webhook operational logs.
    Ideal for onboarding new users or migrating historical data at once.
    """
    db = SessionLocal()
    try:
        events_processed = 0
        for payload in payloads:
            # 1. Upsert Endpoint Data
            endpoint = db.query(Endpoint).filter(Endpoint.endpoint_id == payload.endpoint.endpoint_id).first()
            if not endpoint:
                endpoint = Endpoint(
                    endpoint_id=payload.endpoint.endpoint_id,
                    customer_id=payload.customer_id,
                    endpoint_url_type="custom",
                    expected_signature_version="v1",
                    avg_success_rate=payload.endpoint.avg_success_rate,
                    rate_limit_per_minute=payload.endpoint.rate_limit_per_minute,
                    active=payload.endpoint.active,
                    user_id=user_id
                )
                db.add(endpoint)
            else:
                endpoint.avg_success_rate = payload.endpoint.avg_success_rate
                endpoint.rate_limit_per_minute = payload.endpoint.rate_limit_per_minute
                endpoint.active = payload.endpoint.active
                endpoint.user_id = user_id
                
            # 2. Upsert Webhook Event Data
            event = db.query(WebhookEvent).filter(WebhookEvent.event_id == payload.event_id).first()
            if not event:
                event = WebhookEvent(
                    event_id=payload.event_id,
                    event_type=payload.event_type,
                    customer_id=payload.customer_id,
                    payload_size_kb=250.0,
                    idempotency_key=f"idem_{uuid.uuid4().hex[:8]}",
                    priority="medium",
                    user_id=user_id
                )
                db.add(event)
                
            db.commit() # Flush so attempts can safely reference event_id and endpoint_id
            
            # 3. Store Delivery Attempts
            for attempt in payload.delivery_attempts:
                existing_attempt = db.query(DeliveryAttempt).filter(
                    DeliveryAttempt.event_id == payload.event_id,
                    DeliveryAttempt.attempt_number == attempt.attempt_number
                ).first()
                
                if not existing_attempt:
                    new_attempt = DeliveryAttempt(
                        attempt_id=f"att_{uuid.uuid4().hex[:8]}",
                        event_id=payload.event_id,
                        endpoint_id=payload.endpoint.endpoint_id,
                        attempt_number=attempt.attempt_number,
                        http_status=attempt.http_status,
                        response_time_ms=attempt.response_time_ms,
                        timeout=attempt.timeout,
                        signature_valid=attempt.signature_valid,
                        user_id=user_id
                    )
                    db.add(new_attempt)
                    
            # 4. Store Replay History
            if payload.replay_history and payload.replay_history.previous_replays > 0:
                for i in range(payload.replay_history.previous_replays):
                    new_replay = ReplayAction(
                        replay_id=f"rep_{uuid.uuid4().hex[:8]}",
                        event_id=payload.event_id,
                        replay_result="failed" if payload.delivery_attempts[-1].http_status >= 400 else "success",
                        duplicate_detected=payload.replay_history.duplicate_detected,
                        manually_triggered=payload.replay_history.manually_triggered,
                        user_id=user_id
                    )
                    db.add(new_replay)

            events_processed += 1

        db.commit()
        return {
            "status": "success", 
            "message": f"Successfully processed {events_processed} webhook logs.",
            "user_id": user_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk upload failed: {str(e)}")
    finally:
        db.close()


from fastapi import BackgroundTasks

UPLOAD_STATUS = {}

def process_csv_background(task_id: str, df: pd.DataFrame, user_id: str):
    db = SessionLocal()
    try:
        grouped = list(df.groupby('event_id'))
        UPLOAD_STATUS[task_id]["total"] = len(grouped)
        events_processed = 0
        attempts_processed = 0
        
        for event_id, group in grouped:
            first_row = group.iloc[0]
            
            # 1. Upsert Endpoint
            endpoint = db.query(Endpoint).filter(Endpoint.endpoint_id == first_row['endpoint_id']).first()
            if not endpoint:
                endpoint = Endpoint(
                    endpoint_id=first_row['endpoint_id'],
                    customer_id=first_row['customer_id'],
                    endpoint_url_type="custom",
                    expected_signature_version="v1",
                    avg_success_rate=0.9,
                    rate_limit_per_minute=100,
                    active=True,
                    user_id=user_id
                )
                db.add(endpoint)
                
            # 2. Upsert Webhook Event
            event = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
            if not event:
                event = WebhookEvent(
                    event_id=event_id,
                    event_type=first_row['event_type'],
                    customer_id=first_row['customer_id'],
                    payload_size_kb=250.0,
                    idempotency_key=f"idem_{uuid.uuid4().hex[:8]}",
                    priority="medium",
                    user_id=user_id
                )
                db.add(event)
                
            db.commit()
            
            # 3. Store Delivery Attempts
            for _, attempt_row in group.iterrows():
                attempt_num = int(attempt_row['attempt_number'])
                existing_attempt = db.query(DeliveryAttempt).filter(
                    DeliveryAttempt.event_id == event_id,
                    DeliveryAttempt.attempt_number == attempt_num
                ).first()
                
                if not existing_attempt:
                    new_attempt = DeliveryAttempt(
                        attempt_id=f"att_{uuid.uuid4().hex[:8]}",
                        event_id=event_id,
                        endpoint_id=first_row['endpoint_id'],
                        attempt_number=attempt_num,
                        http_status=int(attempt_row['http_status']) if pd.notna(attempt_row['http_status']) else 500,
                        response_time_ms=float(attempt_row['response_time_ms']) if pd.notna(attempt_row['response_time_ms']) else 1000.0,
                        timeout=str(attempt_row['timeout']).lower() == 'true',
                        signature_valid=str(attempt_row['signature_valid']).lower() == 'true',
                        user_id=user_id
                    )
                    db.add(new_attempt)
                    attempts_processed += 1
            
            events_processed += 1
            
            if events_processed % 5 == 0:
                UPLOAD_STATUS[task_id]["processed"] = events_processed
            
        db.commit()
        UPLOAD_STATUS[task_id]["status"] = "complete"
        UPLOAD_STATUS[task_id]["processed"] = events_processed
        UPLOAD_STATUS[task_id]["attempts_processed"] = attempts_processed
        
        # Send email summary
        try:
            from app.services.mailer import send_upload_summary
            send_upload_summary(user_id, events_processed, attempts_processed)
        except Exception as e:
            print(f"Failed to send email summary: {e}")
        
    except Exception as e:
        db.rollback()
        UPLOAD_STATUS[task_id]["status"] = "failed"
        UPLOAD_STATUS[task_id]["error"] = str(e)
    finally:
        db.close()


@router.post("/upload/csv")
async def upload_webhook_csv(user_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Uploads a flat CSV file and triggers a background task to process it.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
    required_cols = ['event_id', 'event_type', 'customer_id', 'endpoint_id', 'attempt_number', 'http_status', 'response_time_ms', 'timeout', 'signature_valid']
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")
            
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    UPLOAD_STATUS[task_id] = {
        "status": "processing", 
        "processed": 0, 
        "total": len(df['event_id'].unique())
    }
    
    background_tasks.add_task(process_csv_background, task_id, df, user_id)
    return {"status": "accepted", "task_id": task_id}


@router.get("/upload/status/{task_id}")
def get_upload_status(task_id: str):
    """
    Polls the progress of an async CSV upload.
    """
    if task_id not in UPLOAD_STATUS:
        raise HTTPException(status_code=404, detail="Task not found")
    return UPLOAD_STATUS[task_id]


@router.post("/{event_id}/send-mail")
def send_event_analysis_mail(event_id: str, user_id: str):
    """
    Sends the analysis of a specific event to the user's email.
    """
    from app.services.intelligence import get_event_intelligence
    from app.services.mailer import send_event_analysis
    
    try:
        # Get intelligence analysis
        analysis = get_event_intelligence(event_id)
        
        # Send email
        success = send_event_analysis(user_id, event_id, analysis)
        
        if success:
            return {"status": "success", "message": "Email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
