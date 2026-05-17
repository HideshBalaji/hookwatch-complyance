from fastapi import APIRouter
from app.services.analytics import AnalyticsEngine

router = APIRouter()

@router.get("/analytics/endpoints/instability")
async def get_instability():
    """
    Returns the top unstable endpoints ranked by failure rate.
    """
    df = AnalyticsEngine.get_endpoint_instability()
    # Replace NaN/inf with None for JSON serialization
    df = df.replace([float('inf'), float('-inf')], None).fillna(0)
    return {"endpoints": df.to_dict(orient="records")}

@router.get("/analytics/retry/patterns")
async def get_retry_patterns():
    """
    Returns success rate and response time grouped by attempt number.
    """
    df = AnalyticsEngine.get_event_retry_patterns()
    df = df.replace([float('inf'), float('-inf')], None).fillna(0)
    return {"patterns": df.to_dict(orient="records")}

@router.get("/analytics/replays")
async def get_replay_metrics():
    """
    Returns overarching metrics about replay actions.
    """
    df = AnalyticsEngine.get_replay_frequency()
    df = df.replace([float('inf'), float('-inf')], None).fillna(0)
    return {"replays": df.to_dict(orient="records")}
