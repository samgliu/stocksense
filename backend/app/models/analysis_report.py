from sqlalchemy import Column, ForeignKey, DateTime, String, Float, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("stock_entries.id"), nullable=False
    )
    model_version = Column(String, nullable=True)

    current_price = Column(Float, nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    avg_price = Column(Float, nullable=True)
    time_horizon = Column(String, default="30d")

    prediction_json = Column(JSONB, nullable=False)
    insights = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock_entry = relationship("StockEntry", backref="analysis_reports")
