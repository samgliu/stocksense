from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class JobStatusSchema(BaseModel):
    id: UUID
    job_id: str
    user_id: UUID
    analysis_report_id: Optional[UUID] = None
    status: str
    input: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    analysis_report_id: Optional[UUID] = None
    updated_at: datetime

    class Config:
        from_attributes = True
