from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class TradeDecision(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class TradeReport(Base):
    __tablename__ = "trade_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(
        UUID(as_uuid=True), ForeignKey("auto_trade_subscriptions.id")
    )
    user_id = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    ticker = Column(String, nullable=False)
    decision = Column(Enum(TradeDecision), nullable=False)
    reason = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
