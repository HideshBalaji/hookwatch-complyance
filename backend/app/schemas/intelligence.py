from pydantic import BaseModel
from typing import Optional, List

class WebhookEndpointSchema(BaseModel):
    endpoint_id: str
    avg_success_rate: float
    active: bool
    rate_limit_per_minute: int

class DeliveryAttemptSchema(BaseModel):
    attempt_number: int
    http_status: int
    response_time_ms: int
    timeout: bool
    signature_valid: bool
    attempted_at: str

class ReplayHistorySchema(BaseModel):
    previous_replays: int
    duplicate_detected: bool
    manually_triggered: bool

class RawWebhookLogRequest(BaseModel):
    event_id: str
    event_type: str
    customer_id: str
    endpoint: WebhookEndpointSchema
    delivery_attempts: List[DeliveryAttemptSchema]
    replay_history: Optional[ReplayHistorySchema] = None
