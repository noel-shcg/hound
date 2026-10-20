from datetime import datetime, date, timedelta
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from calendar import monthrange, weekday
import calendar


class RecurrenceService:
    """Service for calculating recurring event occurrences."""
    
    @staticmethod
    def generate_occurrences(
        start_date: date,
        frequency: str,
        interval: int = 1,
        weekdays: Optional[List[int]] = None,
        end_date: Optional[date] = None,
        occurrence_limit: Optional[int] = None,
        range_start: Optional[date] = None,
        range_end: Optional[date] = None
    ) -> List[date]:
        """
        Generate occurrences of a recurring event.
        
        Args:
            start_date: The start date of the recurrence
            frequency: 'daily', 'weekly', 'monthly', 'yearly'
            interval: Every N days/weeks/months/years
            weekdays: List of weekday numbers (0=Monday, 6=Sunday) for weekly recurrence
            end_date: End date for the recurrence
            occurrence_limit: Maximum number of occurrences
            range_start: Start of date range to return
            range_end: End of date range to return
        
        Returns:
            List of occurrence dates
        """
        occurrences = []
        current_date = start_date
        count = 0
        
        if range_start is None:
            range_start = start_date
        if range_end is None:
            range_end = date(2099, 12, 31)
        
        # Generate occurrences until we exceed limits
        while True:
            # Check if we've exceeded the range
            if current_date > range_end:
                break
            
            # Check if we've exceeded the end date
            if end_date and current_date > end_date:
                break
            
            # Check if we've exceeded the occurrence limit
            if occurrence_limit and count >= occurrence_limit:
                break
            
            # Check if this occurrence is within the range
            if current_date >= range_start:
                # For weekly with specific weekdays, check if current date matches
                if frequency == "weekly" and weekdays:
                    if current_date.weekday() in weekdays:
                        occurrences.append(current_date)
                        count += 1
                else:
                    occurrences.append(current_date)
                    count += 1
            
            # Calculate next occurrence
            if frequency == "daily":
                current_date += timedelta(days=interval)
            elif frequency == "weekly":
                if weekdays:
                    # Find next matching weekday
                    current_date = RecurrenceService._next_weekday(current_date, weekdays, interval)
                else:
                    current_date += timedelta(weeks=interval)
            elif frequency == "monthly":
                current_date += relativedelta(months=interval)
            elif frequency == "yearly":
                current_date += relativedelta(years=interval)
            else:
                break
        
        return occurrences
    
    @staticmethod
    def _next_weekday(current_date: date, weekdays: List[int], interval: int) -> date:
        """Find the next date matching one of the specified weekdays."""
        current_weekday = current_date.weekday()
        
        # Sort weekdays
        sorted_weekdays = sorted(weekdays)
        
        # Find the next weekday in the current week
        for wd in sorted_weekdays:
            if wd > current_weekday:
                return current_date + timedelta(days=wd - current_weekday)
        
        # If no weekday in current week, move to next interval
        # and find the first matching weekday
        next_week_start = current_date + timedelta(weeks=interval)
        next_week_start = next_week_start - timedelta(days=next_week_start.weekday())
        
        return next_week_start + timedelta(days=sorted_weekdays[0])
    
    @staticmethod
    def get_occurrences_for_range(
        event_start: datetime,
        frequency: str,
        interval: int = 1,
        weekdays: Optional[List[int]] = None,
        end_date: Optional[datetime] = None,
        occurrence_limit: Optional[int] = None,
        range_start: date = None,
        range_end: date = None
    ) -> List[datetime]:
        """
        Get occurrences for a specific date range, preserving time.
        
        Args:
            event_start: The start datetime of the event
            frequency: 'daily', 'weekly', 'monthly', 'yearly'
            interval: Every N days/weeks/months/years
            weekdays: List of weekday numbers for weekly recurrence
            end_date: End datetime for the recurrence
            occurrence_limit: Maximum number of occurrences
            range_start: Start of date range
            range_end: End of date range
        
        Returns:
            List of occurrence datetimes
        """
        event_date = event_start.date()
        event_time = event_start.time()
        
        # Handle all-day events (time at midnight)
        if event_time.hour == 0 and event_time.minute == 0:
            event_date_only = True
        else:
            event_date_only = False
        
        # Convert end_date to date if it's a datetime
        end_date_only = end_date.date() if end_date else None
        
        occurrences = RecurrenceService.generate_occurrences(
            start_date=event_date,
            frequency=frequency,
            interval=interval,
            weekdays=weekdays,
            end_date=end_date_only,
            occurrence_limit=occurrence_limit,
            range_start=range_start,
            range_end=range_end
        )
        
        # Convert back to datetime, preserving time
        result = []
        for occ_date in occurrences:
            if event_date_only:
                # All-day event: keep at midnight
                result.append(datetime.combine(occ_date, event_time))
            else:
                # Timed event: preserve the original time
                result.append(datetime.combine(occ_date, event_time))
        
        return result
    
    @staticmethod
    def get_next_occurrence(
        event_start: datetime,
        frequency: str,
        interval: int = 1,
        weekdays: Optional[List[int]] = None,
        end_date: Optional[datetime] = None,
        occurrence_limit: Optional[int] = None,
        after_date: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        Get the next occurrence after a specific date.
        """
        if after_date is None:
            after_date = datetime.utcnow()
        
        occurrences = RecurrenceService.get_occurrences_for_range(
            event_start=event_start,
            frequency=frequency,
            interval=interval,
            weekdays=weekdays,
            end_date=end_date,
            occurrence_limit=occurrence_limit,
            range_start=after_date.date(),
            range_end=after_date.date() + timedelta(days=365)  # Look ahead 1 year
        )
        
        # Find first occurrence after after_date
        for occ in occurrences:
            if occ > after_date:
                return occ
        
        return None


# Singleton instance
recurrence_service = RecurrenceService()
