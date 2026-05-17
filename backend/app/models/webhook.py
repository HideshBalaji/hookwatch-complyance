from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.db import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    events = relationship("WebhookEvent", back_populates="user")
    endpoints = relationship("Endpoint", back_populates="user")
    attempts = relationship("DeliveryAttempt", back_populates="user")
    replays = relationship("ReplayAction", back_populates="user")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    event_id = Column(String, primary_key=True, index=True)
    event_type = Column(String, index=True)
    customer_id = Column(String, index=True)
    invoice_id = Column(String)
    payload_size_kb = Column(Float)
    idempotency_key = Column(String, unique=True, index=True)
    priority = Column(String)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attempts = relationship("DeliveryAttempt", back_populates="event")
    replays = relationship("ReplayAction", back_populates="event")
    user = relationship("User", back_populates="events")


class Endpoint(Base):
    __tablename__ = "endpoints"

    endpoint_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    endpoint_url_type = Column(String)
    expected_signature_version = Column(String)
    avg_success_rate = Column(Float)
    rate_limit_per_minute = Column(Integer)
    active = Column(Boolean, default=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    last_config_change_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attempts = relationship("DeliveryAttempt", back_populates="endpoint")
    user = relationship("User", back_populates="endpoints")


class DeliveryAttempt(Base):
    __tablename__ = "delivery_attempts"

    attempt_id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("webhook_events.event_id"))
    endpoint_id = Column(String, ForeignKey("endpoints.endpoint_id"))
    attempt_number = Column(Integer)
    http_status = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    response_body_category = Column(String)
    timeout = Column(Boolean, default=False)
    signature_valid = Column(Boolean, nullable=True)
    retry_scheduled = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    attempted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("WebhookEvent", back_populates="attempts")
    endpoint = relationship("Endpoint", back_populates="attempts")
    user = relationship("User", back_populates="attempts")


class ReplayAction(Base):
    __tablename__ = "replay_actions"

    # CSV does not have a primary key column, so we generate a UUID
    replay_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    event_id = Column(String, ForeignKey("webhook_events.event_id"))
    replay_result = Column(String)
    duplicate_detected = Column(Boolean, default=False)
    manually_triggered = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    replayed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    event = relationship("WebhookEvent", back_populates="replays")
    user = relationship("User", back_populates="replays")
