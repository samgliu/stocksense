from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_entry_id = Column(UUID(as_uuid=True), ForeignKey("stock_entries.id"), nullable=False)
    model = Column(String, nullable=True)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock_entry = relationship("StockEntry", backref="predictions")
