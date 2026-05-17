from fastapi import APIRouter
from app.services.intelligence import get_event_intelligence

router = APIRouter()

@router.get("/intelligence/{event_id}")
async def fetch_intelligence(event_id: str):
    """
    Returns AI-powered intelligence about a specific webhook event.
    Predicts if a failed event is safe to replay, detects anomalies, 
    and issues operational recommendations.
    """
    return get_event_intelligence(event_id)
