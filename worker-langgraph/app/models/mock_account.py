from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class MockAccount(Base):
    __tablename__ = "mock_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    balance = Column(Float, default=1000000.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
