from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class JobStatusSchema(BaseModel):
    job_id: str
    status: str
    result: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
