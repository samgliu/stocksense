from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import uuid


class JobStatus(Base):
    __tablename__ = "job_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, default="queued")  # queued, processing, done, error
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
