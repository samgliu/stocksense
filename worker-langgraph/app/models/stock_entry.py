import uuid
from sqlalchemy import Column, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# free text analysis entry
class StockEntry(Base):
    __tablename__ = "stock_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    text_input = Column(Text, nullable=True)
    file_name = Column(String, nullable=True)
    file_content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    model_used = Column(String, nullable=True, default="gemini")
    source_type = Column(String, nullable=True, default="text")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="stock_entries")
    company = relationship("Company", backref="stock_entries")
