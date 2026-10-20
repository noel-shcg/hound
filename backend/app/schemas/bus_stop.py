from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BusStopBase(BaseModel):
    atco_code: str
    custom_label: str
    official_name: Optional[str] = None
    enabled: bool = True
    display_order: int = 0


class BusStopCreate(BusStopBase):
    pass


class BusStopUpdate(BaseModel):
    custom_label: Optional[str] = None
    official_name: Optional[str] = None
    enabled: Optional[bool] = None
    display_order: Optional[int] = None


class BusStopResponse(BusStopBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusDeparture(BaseModel):
    route: Optional[str] = None
    destination: Optional[str] = None
    scheduled_time: Optional[str] = None
    countdown_minutes: Optional[int] = None
    status: Optional[str] = None
