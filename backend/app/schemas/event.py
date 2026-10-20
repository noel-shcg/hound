from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any


class EventBase(BaseModel):
    title: str
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    all_day: bool = False
    notes: Optional[str] = None
    category_id: Optional[int] = None


class EventCreate(EventBase):
    is_recurring: bool = False
    recurrence_rule: Optional[dict] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    all_day: Optional[bool] = None
    notes: Optional[str] = None
    category_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    is_recurring: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Any] = None
    recurrence_rule: Optional[Any] = None

    class Config:
        from_attributes = True


class RecurrenceRuleBase(BaseModel):
    frequency: str  # daily, weekly, monthly, yearly
    interval: int = 1
    weekdays: Optional[List[int]] = None  # 0-6 for Mon-Sun
    end_date: Optional[datetime] = None
    occurrence_limit: Optional[int] = None


class RecurrenceRuleCreate(RecurrenceRuleBase):
    pass


class RecurrenceRuleUpdate(BaseModel):
    frequency: Optional[str] = None
    interval: Optional[int] = None
    weekdays: Optional[List[int]] = None
    end_date: Optional[datetime] = None
    occurrence_limit: Optional[int] = None


class RecurrenceRuleResponse(RecurrenceRuleBase):
    id: int
    event_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
