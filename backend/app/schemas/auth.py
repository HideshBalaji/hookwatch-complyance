from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    name: str

class WebhookListResponse(BaseModel):
    event_id: str
    event_type: str
    created_at: datetime
    endpoint_id: Optional[str] = None
