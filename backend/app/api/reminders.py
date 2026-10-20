from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.reminder import Reminder
from ..schemas.reminder import ReminderCreate, ReminderUpdate, ReminderResponse

router = APIRouter()


@router.get("/", response_model=List[ReminderResponse])
async def list_reminders(db: Session = Depends(get_db)):
    """List all reminders."""
    reminders = db.query(Reminder).all()
    return reminders


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Get a specific reminder."""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.post("/", response_model=ReminderResponse)
async def create_reminder(reminder_data: ReminderCreate, db: Session = Depends(get_db)):
    """Create a new reminder."""
    reminder = Reminder(**reminder_data.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(reminder_id: int, reminder_data: ReminderUpdate, db: Session = Depends(get_db)):
    """Update a reminder (typically to mark as completed)."""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    update_data = reminder_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)
    
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    """Delete a reminder."""
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}
