from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=True)
    all_day = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("event_categories.id"), nullable=True)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("EventCategory", backref="events")
    recurrence_rule = relationship("RecurrenceRule", back_populates="event", uselist=False)


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, unique=True)
    frequency = Column(String, nullable=False)  # daily, weekly, monthly, yearly
    interval = Column(Integer, default=1)  # every N days/weeks/months/years
    weekdays = Column(JSON, nullable=True)  # list of weekday numbers for weekly
    end_date = Column(DateTime(timezone=True), nullable=True)
    occurrence_limit = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    event = relationship("Event", back_populates="recurrence_rule")
