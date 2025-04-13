from pydantic import BaseModel, ConfigDict
from uuid import UUID
from enum import Enum
from datetime import datetime
from typing import Optional


class FrequencyEnum(str, Enum):
    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"


class RiskToleranceEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AutoTradeSubscriptionCreate(BaseModel):
    user_id: str
    company_id: UUID
    ticker: str
    frequency: FrequencyEnum
    risk_tolerance: RiskToleranceEnum
    wash_sale: bool = True


class AutoTradeSubscriptionOut(AutoTradeSubscriptionCreate):
    id: UUID
    created_at: datetime
    last_run_at: Optional[datetime]
    company_name: Optional[str]
    active: bool
    model_config = ConfigDict(from_attributes=True)
