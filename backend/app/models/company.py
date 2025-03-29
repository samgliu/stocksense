from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ticker = Column(String, unique=True, nullable=False)
    exchange = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    country = Column(String, nullable=True, default="USA")
    website = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
