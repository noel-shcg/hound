from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ..core.database import get_db
from ..models.event import Event, RecurrenceRule
from ..schemas.event import EventCreate, EventUpdate, EventResponse

router = APIRouter()


@router.get("/", response_model=List[EventResponse])
async def list_events(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """List events, optionally filtered by date range."""
    query = db.query(Event)
    
    if start_date:
        query = query.filter(Event.start_datetime >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Event.start_datetime <= datetime.combine(end_date, datetime.max.time()))
    
    events = query.order_by(Event.start_datetime).all()
    return events


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a specific event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=EventResponse)
async def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
    recurrence_rule_data = event_data.recurrence_rule
    event_dict = event_data.model_dump(exclude={"recurrence_rule"})
    
    event = Event(**event_dict)
    db.add(event)
    db.flush()  # Get the event ID
    
    if recurrence_rule_data and event_data.is_recurring:
        recurrence_rule = RecurrenceRule(
            event_id=event.id,
            **recurrence_rule_data
        )
        db.add(recurrence_rule)
    
    db.commit()
    db.refresh(event)
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_db)):
    """Update an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Delete an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}


@router.get("/recurring/occurrences")
async def get_recurring_occurrences(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get occurrences of recurring events within a date range."""
    # This will be implemented by the recurrence service
    # For now, return empty list
    return {"occurrences": []}
