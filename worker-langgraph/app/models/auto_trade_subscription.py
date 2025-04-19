from datetime import datetime, timezone
import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class FrequencyEnum(str, enum.Enum):
    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"


class RiskToleranceEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AutoTradeSubscription(Base):
    __tablename__ = "auto_trade_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    ticker = Column(String, nullable=False)

    frequency = Column(Enum(FrequencyEnum), nullable=False)
    risk_tolerance = Column(Enum(RiskToleranceEnum), nullable=False)
    wash_sale = Column(Boolean, default=True)

    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    last_run_at = Column(DateTime(timezone=True), nullable=True)
