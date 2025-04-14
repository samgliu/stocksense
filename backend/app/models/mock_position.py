from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class MockPosition(Base):
    __tablename__ = "mock_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("mock_accounts.id"))
    ticker = Column(String, nullable=False)
    shares = Column(Integer, nullable=False, default=0)
    average_cost = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
