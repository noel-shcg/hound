import pytest
from datetime import date, datetime, timedelta
from app.services.recurrence_service import recurrence_service


class TestRecurrenceService:
    """Tests for recurrence calculation."""
    
    def test_daily_recurrence(self):
        """Test daily recurrence generation."""
        start_date = date(2024, 1, 1)
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="daily",
            interval=1,
            range_start=date(2024, 1, 1),
            range_end=date(2024, 1, 7)
        )
        
        assert len(occurrences) == 7
        assert occurrences[0] == date(2024, 1, 1)
        assert occurrences[-1] == date(2024, 1, 7)
    
    def test_weekly_recurrence(self):
        """Test weekly recurrence generation."""
        start_date = date(2024, 1, 1)  # Monday
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="weekly",
            interval=1,
            range_start=date(2024, 1, 1),
            range_end=date(2024, 1, 31)
        )
        
        assert len(occurrences) == 5  # 5 Mondays in January 2024
        assert all(occ.weekday() == 0 for occ in occurrences)
    
    def test_weekly_specific_weekdays(self):
        """Test weekly recurrence with specific weekdays."""
        start_date = date(2024, 1, 1)  # Monday
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="weekly",
            interval=1,
            weekdays=[0, 2, 4],  # Monday, Wednesday, Friday
            range_start=date(2024, 1, 1),
            range_end=date(2024, 1, 14)
        )
        
        # Should have 6 occurrences (2 per week for 2 weeks)
        assert len(occurrences) == 6
        assert all(occ.weekday() in [0, 2, 4] for occ in occurrences)
    
    def test_monthly_recurrence(self):
        """Test monthly recurrence generation."""
        start_date = date(2024, 1, 15)
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="monthly",
            interval=1,
            range_start=date(2024, 1, 1),
            range_end=date(2024, 6, 30)
        )
        
        assert len(occurrences) == 6
        assert all(occ.day == 15 for occ in occurrences)
    
    def test_yearly_recurrence(self):
        """Test yearly recurrence generation."""
        start_date = date(2020, 3, 15)
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="yearly",
            interval=1,
            range_start=date(2020, 1, 1),
            range_end=date(2024, 12, 31)
        )
        
        assert len(occurrences) == 5
        assert all(occ.month == 3 and occ.day == 15 for occ in occurrences)
    
    def test_end_date(self):
        """Test recurrence with end date."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 10)
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="daily",
            interval=1,
            end_date=end_date,
            range_start=date(2024, 1, 1),
            range_end=date(2024, 1, 31)
        )
        
        assert len(occurrences) == 10
        assert occurrences[-1] == end_date
    
    def test_occurrence_limit(self):
        """Test recurrence with occurrence limit."""
        start_date = date(2024, 1, 1)
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="daily",
            interval=1,
            occurrence_limit=5,
            range_start=date(2024, 1, 1),
            range_end=date(2024, 1, 31)
        )
        
        assert len(occurrences) == 5
    
    def test_leap_year(self):
        """Test recurrence handles leap years correctly."""
        start_date = date(2020, 2, 29)  # Leap year
        occurrences = recurrence_service.generate_occurrences(
            start_date=start_date,
            frequency="yearly",
            interval=1,
            range_start=date(2020, 1, 1),
            range_end=date(2024, 12, 31)
        )
        
        # 2020, 2024 are leap years
        # 2021, 2022, 2023 are not - should land on March 1
        assert len(occurrences) == 5
        assert occurrences[0] == date(2020, 2, 29)
        assert occurrences[1] == date(2021, 3, 1)
        assert occurrences[4] == date(2024, 2, 29)
    
    def test_get_occurrences_for_range_preserves_time(self):
        """Test that time is preserved in datetime occurrences."""
        start_datetime = datetime(2024, 1, 1, 14, 30)
        occurrences = recurrence_service.get_occurrences_for_range(
            event_start=start_datetime,
            frequency="daily",
            interval=1,
            range_start=date(2024, 1, 1),
            range_end=date(2024, 1, 3)
        )
        
        assert len(occurrences) == 3
        assert all(occ.hour == 14 and occ.minute == 30 for occ in occurrences)
