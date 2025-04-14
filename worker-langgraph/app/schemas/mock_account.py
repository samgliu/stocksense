from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class MockAccountBase(BaseModel):
    user_id: str
    balance: float = 1000000.0


class MockAccountOut(MockAccountBase):
    id: UUID
    created_at: datetime
