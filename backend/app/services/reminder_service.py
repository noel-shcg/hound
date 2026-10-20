from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.event import Event, RecurrenceRule
from ..models.reminder import Reminder
from ..services.recurrence_service import recurrence_service


class ReminderService:
    """Service for managing reminders and evaluating when they become relevant."""
    
    @staticmethod
    def get_active_reminders(db: Session, as_of: Optional[datetime] = None) -> List[Reminder]:
        """
        Get reminders that are currently active (not completed and past their trigger time).
        """
        if as_of is None:
            as_of = datetime.utcnow()
        
        reminders = db.query(Reminder).filter(
            Reminder.completed == False
        ).all()
        
        active_reminders = []
        for reminder in reminders:
            event = db.query(Event).filter(Event.id == reminder.event_id).first()
            if not event:
                continue
            
            # Calculate trigger time
            if event.is_recurring and reminder.for_occurrence_date:
                # For recurring events with specific occurrence
                trigger_time = reminder.for_occurrence_date - timedelta(minutes=reminder.minutes_before)
            else:
                # For one-off events
                trigger_time = event.start_datetime - timedelta(minutes=reminder.minutes_before)
            
            # Check if reminder is now relevant
            if trigger_time <= as_of:
                active_reminders.append(reminder)
        
        return active_reminders
    
    @staticmethod
    def create_reminders_for_event(db: Session, event: Event) -> List[Reminder]:
        """
        Create reminders for an event based on its reminder configuration.
        This is a placeholder - in the full implementation, reminder times would be
        configured on the event itself.
        """
        # For now, we'll create a default reminder 30 minutes before
        # In the full implementation, this would read from event.reminder_times
        reminder = Reminder(
            event_id=event.id,
            minutes_before=30,
            completed=False
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        return [reminder]
    
    @staticmethod
    def create_reminders_for_recurring_occurrence(
        db: Session,
        event: Event,
        occurrence_date: datetime
    ) -> List[Reminder]:
        """
        Create reminders for a specific occurrence of a recurring event.
        """
        # Get the reminder template from the base event
        base_reminders = db.query(Reminder).filter(
            Reminder.event_id == event.id,
            Reminder.for_occurrence_date.is_(None)
        ).all()
        
        new_reminders = []
        for base_reminder in base_reminders:
            # Create a reminder for this specific occurrence
            reminder = Reminder(
                event_id=event.id,
                minutes_before=base_reminder.minutes_before,
                completed=False,
                for_occurrence_date=occurrence_date
            )
            db.add(reminder)
            new_reminders.append(reminder)
        
        db.commit()
        
        return new_reminders
    
    @staticmethod
    def mark_completed(db: Session, reminder_id: int) -> Reminder:
        """Mark a reminder as completed."""
        reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
        if not reminder:
            return None
        
        reminder.completed = True
        reminder.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(reminder)
        
        return reminder
    
    @staticmethod
    def evaluate_recurring_reminders(db: Session, days_ahead: int = 7):
        """
        Evaluate recurring events and create reminders for upcoming occurrences.
        This should be called periodically.
        """
        as_of = datetime.utcnow()
        range_end = as_of + timedelta(days=days_ahead)
        
        # Get all recurring events
        recurring_events = db.query(Event).filter(Event.is_recurring == True).all()
        
        for event in recurring_events:
            if not event.recurrence_rule:
                continue
            
            # Get occurrences for the next week
            occurrences = recurrence_service.get_occurrences_for_range(
                event_start=event.start_datetime,
                frequency=event.recurrence_rule.frequency,
                interval=event.recurrence_rule.interval,
                weekdays=event.recurrence_rule.weekdays,
                end_date=event.recurrence_rule.end_date,
                occurrence_limit=event.recurrence_rule.occurrence_limit,
                range_start=as_of.date(),
                range_end=range_end.date()
            )
            
            # Create reminders for each occurrence if they don't exist
            for occurrence in occurrences:
                existing = db.query(Reminder).filter(
                    Reminder.event_id == event.id,
                    Reminder.for_occurrence_date == occurrence
                ).first()
                
                if not existing:
                    ReminderService.create_reminders_for_recurring_occurrence(
                        db, event, occurrence
                    )


# Singleton instance
reminder_service = ReminderService()
