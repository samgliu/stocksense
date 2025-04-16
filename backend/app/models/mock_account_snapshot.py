from sqlalchemy import Column, String, Date, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class MockAccountSnapshot(Base):
    __tablename__ = "mock_account_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("mock_accounts.id"), nullable=False)
    user_id = Column(String, nullable=False)
    date = Column(Date, nullable=False, index=True)
    balance = Column(Float, nullable=False)  # Cash balance
    portfolio_value = Column(Float, nullable=False)  # Value of all positions
    total_value = Column(Float, nullable=False)  # balance + portfolio_value
    return_pct = Column(Float, nullable=False)  # (total_value / initial_balance - 1)
