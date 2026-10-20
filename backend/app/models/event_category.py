from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class EventCategory(Base):
    __tablename__ = "event_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    colour = Column(String, nullable=False, default="#4A90E2")
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
