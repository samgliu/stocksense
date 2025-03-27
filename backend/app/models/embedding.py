from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from app.database import Base

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_entry_id = Column(UUID(as_uuid=True), ForeignKey("stock_entries.id"), nullable=False)
    vector = Column(JSON, nullable=False)
    model = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock_entry = relationship("StockEntry", backref="embeddings")
