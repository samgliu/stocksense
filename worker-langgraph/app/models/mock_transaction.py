from sqlalchemy import Column, String, DateTime, Float, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
from app.models.trade_report import TradeDecision
import uuid


class MockTransaction(Base):
    __tablename__ = "mock_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("mock_accounts.id"))
    ticker = Column(String, nullable=False)
    action = Column(Enum(TradeDecision), nullable=False)
    amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    realized_gain = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
