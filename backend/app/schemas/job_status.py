from pydantic import BaseModel
from typing import Optional, Union, Dict, Any
from uuid import UUID
from datetime import datetime


class JobStatusSchema(BaseModel):
    id: UUID
    job_id: str
    user_id: UUID
    stock_entry_id: Optional[UUID] = None
    analysis_report_id: Optional[UUID] = None
    status: str
    input: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    input: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    stock_entry_id: Optional[UUID] = None
    analysis_report_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
