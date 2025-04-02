from sqlalchemy import Column, ForeignKey, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class JobStatus(Base):
    __tablename__ = "job_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    analysis_report_id = Column(
        UUID(as_uuid=True), ForeignKey("analysis_reports.id"), nullable=True
    )
    status = Column(String, default="queued")  # queued, processing, done, error
    input = Column(JSONB, nullable=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    analysis_report = relationship("AnalysisReport", backref="job")
