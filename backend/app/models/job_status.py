from sqlalchemy import Column, ForeignKey, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class JobStatus(Base):
    __tablename__ = "job_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    stock_entry_id = Column(
        UUID(as_uuid=True), ForeignKey("stock_entries.id"), nullable=True
    )
    analysis_report_id = Column(
        UUID(as_uuid=True), ForeignKey("analysis_reports.id"), nullable=True
    )

    status = Column(String, default="queued")  # queued, processing, done, error
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    stock_entry = relationship("StockEntry", backref="jobs")
    analysis_report = relationship("AnalysisReport", backref="job")
