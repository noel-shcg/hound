from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReminderBase(BaseModel):
    event_id: int
    minutes_before: int


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    completed: Optional[bool] = None


class ReminderResponse(ReminderBase):
    id: int
    completed: bool
    completed_at: Optional[datetime] = None
    for_occurrence_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
