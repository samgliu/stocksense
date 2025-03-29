from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class UsageLogOut(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    created_at: datetime

    class Config:
        from_attributes = True
