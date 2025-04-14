from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional, Any


class TradeDecision(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class TradeReportBase(BaseModel):
    subscription_id: UUID
    user_id: str
    company_id: UUID
    ticker: str
    decision: TradeDecision
    reason: Optional[str] = None
    payload: Optional[Any] = None


class TradeReportOut(TradeReportBase):
    id: UUID
    created_at: datetime
