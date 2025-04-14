from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class MockPositionBase(BaseModel):
    account_id: UUID
    ticker: str
    shares: int
    average_cost: float


class MockPositionOut(MockPositionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
