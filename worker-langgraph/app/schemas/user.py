from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str]


class UserOut(BaseModel):
    id: UUID
    email: str
    fullname: str
    role: str
    verified: bool
    usage_count_today: int

    class Config:
        from_attributes = True
