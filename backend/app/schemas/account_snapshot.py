from pydantic import BaseModel
from uuid import UUID
from datetime import date

class MockAccountSnapshotBase(BaseModel):
    account_id: UUID
    user_id: str
    date: date
    balance: float
    portfolio_value: float
    total_value: float
    return_pct: float

class MockAccountSnapshotCreate(MockAccountSnapshotBase):
    pass

class MockAccountSnapshotRead(MockAccountSnapshotBase):
    id: UUID

    class Config:
        from_attributes = True
