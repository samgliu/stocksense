from sqlalchemy import Column, String, Float, Numeric, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )

    # Identifiers
    ticker = Column(String, unique=True, nullable=False)  # From "Symbol"
    name = Column(String, nullable=False)  # From "Longname"
    shortname = Column(String, nullable=True)
    exchange = Column(String, nullable=True)

    # Business classification
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True, default="USA")

    # Optional enrichment
    summary = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Financials
    current_price = Column(Numeric, nullable=True)
    market_cap = Column(Numeric, nullable=True)
    ebitda = Column(Numeric, nullable=True)
    revenue_growth = Column(Float, nullable=True)

    # Team
    fulltime_employees = Column(Numeric, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
