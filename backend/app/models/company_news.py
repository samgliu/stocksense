from app.database import Base
from sqlalchemy import Column, String, Text, DateTime, ARRAY, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class CompanyNews(Base):
    __tablename__ = "company_news"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False)
    source = Column(String, nullable=True)
    language = Column(String, nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    relevance_score = Column(String, nullable=True)

    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", backref="company_news")
