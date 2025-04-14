from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum


class TradeDecision(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class MockTransactionBase(BaseModel):
    account_id: UUID
    ticker: str
    action: TradeDecision
    amount: int
    price: float


class MockTransactionOut(MockTransactionBase):
    id: UUID
    timestamp: datetime
