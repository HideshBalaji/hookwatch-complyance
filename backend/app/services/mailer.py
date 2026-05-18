import os
import json
import urllib.request
import urllib.error
from app.database.db import SessionLocal
from app.models.webhook import User, WebhookEvent

def send_email(to_email: str, subject: str, html_content: str):
    api_key = os.getenv("MAILER_KEY")
    if not api_key:
        print("Mailer key not found in environment")
        return False
        
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    data = {
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": subject,
        "html": html_content
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'), 
        headers=headers, 
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode('utf-8')
            print(f"Email sent successfully: {res_data}")
            return True
    except urllib.error.HTTPError as e:
        print(f"Failed to send email: HTTP Error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Resend Error Response: {error_body}")
        except:
            pass
        return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_upload_summary(user_id: str, events_count: int, attempts_count: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user or not user.email:
            print("User or email not found")
            return
            
        # Fetch Analytics Data
        from app.services.analytics import AnalyticsEngine
        
        try:
            instability_df = AnalyticsEngine.get_endpoint_instability().head(3)
            instability_html = "<ul style='margin: 0; padding-left: 20px; font-size: 14px; color: #1f2937;'>"
            for _, row in instability_df.iterrows():
                instability_html += f"<li style='margin-bottom: 4px;'><strong>{row['endpoint_id']}</strong>: {(row['failure_rate']*100):.1f}% fail rate</li>"
            instability_html += "</ul>"
        except Exception as e:
            print(f"Error generating mail instability data: {e}")
            instability_html = "<p style='font-size: 14px; color: #6b7280;'>Insufficient data to rank unstable endpoints.</p>"
            
        try:
            retry_df = AnalyticsEngine.get_event_retry_patterns().head(4)
            retry_html = "<ul style='margin: 0; padding-left: 20px; font-size: 14px; color: #1f2937;'>"
            for _, row in retry_df.iterrows():
                retry_html += f"<li style='margin-bottom: 4px;'><strong>Attempt #{int(row['attempt_number'])}</strong>: {row['success_rate_percent']:.1f}% success</li>"
            retry_html += "</ul>"
        except Exception as e:
            print(f"Error generating mail retry data: {e}")
            retry_html = "<p style='font-size: 14px; color: #6b7280;'>Insufficient retry pattern data.</p>"
            
        subject = "HookWatch - Data Ingestion & Analytics Complete"
        html = f"""
        <div style="font-family: sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px;">
            <h1 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">Hello {user.name},</h1>
            <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">Your webhook data ingestion task has been completed successfully. Here is your initial analytics snapshot:</p>
            
            <div style="background-color: #f9fafb; padding: 16px; border-radius: 6px; margin: 20px 0;">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #111827;">Ingestion Stats</h3>
                <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #1f2937;">
                    <li style="margin-bottom: 4px;"><strong>Unique Events Processed:</strong> {events_count}</li>
                    <li><strong>Delivery Attempts Stored:</strong> {attempts_count}</li>
                </ul>
            </div>
            
            <div style="background-color: #f9fafb; padding: 16px; border-radius: 6px; margin: 20px 0;">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #111827;">Top Unstable Endpoints</h3>
                {instability_html}
            </div>
            
            <div style="background-color: #f9fafb; padding: 16px; border-radius: 6px; margin: 20px 0;">
                <h3 style="font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #111827;">Retry Effectiveness</h3>
                {retry_html}
            </div>
            
            <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">You can view the full interactive breakdown in your dashboard.</p>
            <p style="font-size: 12px; color: #9ca3af; margin-top: 32px;">Best regards,<br/>HookWatch Team</p>
        </div>
        """
        send_email(user.email, subject, html)
    finally:
        db.close()

def send_event_analysis(user_id: str, event_id: str, analysis: dict):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user or not user.email:
            return False
            
        subject = f"HookWatch - Analysis for Event {event_id}"
        html = f"""
        <div style="font-family: sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px;">
            <h1 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">Hello {user.name},</h1>
            <p style="font-size: 14px; line-height: 1.5; color: #4b5563;">Here is the requested analysis for event <strong>{event_id}</strong>.</p>
            
            <div style="background-color: #f9fafb; padding: 16px; border-radius: 6px; margin: 20px 0;">
                <h2 style="font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #111827;">Model Analysis</h2>
                <p style="font-size: 14px; margin-bottom: 8px;"><strong>Replay Safety:</strong> {analysis.get('safe_to_replay', False)}</p>
                <p style="font-size: 14px; margin-bottom: 8px;"><strong>Is Anomaly:</strong> {analysis.get('is_anomaly', False)}</p>
                <p style="font-size: 14px; margin-bottom: 8px;"><strong>Recommended Action:</strong> {analysis.get('recommended_action', 'N/A')}</p>
                <p style="font-size: 14px; margin-bottom: 0;"><strong>Endpoint Health:</strong> {analysis.get('metrics', {}).get('endpoint_health', 'N/A')}</p>
            </div>
            
            <p style="font-size: 12px; color: #9ca3af; margin-top: 32px;">Best regards,<br/>HookWatch Team</p>
        </div>
        """
        return send_email(user.email, subject, html)
    finally:
        db.close()
