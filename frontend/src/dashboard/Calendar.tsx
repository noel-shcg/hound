import { useEffect, useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameDay, isToday } from 'date-fns';
import { eventsApi, Event } from '../api/events';

interface CalendarProps {
  className?: string;
  month?: number;
  year?: number;
}

export const Calendar: React.FC<CalendarProps> = ({ className = '', month, year }) => {
  const currentDate = new Date();
  const displayMonth = month ?? currentDate.getMonth();
  const displayYear = year ?? currentDate.getFullYear();
  
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const monthStart = startOfMonth(new Date(displayYear, displayMonth));
        const monthEnd = endOfMonth(new Date(displayYear, displayMonth));
        const data = await eventsApi.list(
          monthStart.toISOString(),
          monthEnd.toISOString()
        );
        setEvents(data);
      } catch (err) {
        console.error('Failed to load events:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [displayMonth, displayYear]);

  const monthStart = startOfMonth(new Date(displayYear, displayMonth));
  const monthEnd = endOfMonth(new Date(displayYear, displayMonth));
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });
  
  // Get day of week for the first day (0 = Sunday, 1 = Monday, etc.)
  const startDayOfWeek = monthStart.getDay();
  
  // Create calendar grid with padding days
  const calendarDays = [];
  for (let i = 0; i < startDayOfWeek; i++) {
    calendarDays.push(null); // Empty cells for padding
  }
  calendarDays.push(...days);

  const getEventsForDay = (date: Date) => {
    return events.filter(event => {
      const eventDate = new Date(event.start_datetime);
      return isSameDay(eventDate, date);
    });
  };

  return (
    <div className={`calendar ${className}`}>
      <div className="calendar-header">
        <h2 className="calendar-title">
          {format(new Date(displayYear, displayMonth), 'MMMM yyyy')}
        </h2>
      </div>
      <div className="calendar-grid">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
          <div key={day} className="calendar-day-header">
            {day}
          </div>
        ))}
        {calendarDays.map((date, idx) => {
          if (!date) {
            return <div key={`empty-${idx}`} className="calendar-day empty" />;
          }
          
          const dayEvents = getEventsForDay(date);
          const isTodayDate = isToday(date);
          
          return (
            <div
              key={date.toISOString()}
              className={`calendar-day ${isTodayDate ? 'today' : ''} ${dayEvents.length > 0 ? 'has-events' : ''}`}
            >
              <div className="calendar-day-number">{date.getDate()}</div>
              {dayEvents.slice(0, 3).map((event, eventIdx) => (
                <div
                  key={eventIdx}
                  className="calendar-event"
                  style={{
                    backgroundColor: event.category?.colour || '#4A90E2'
                  }}
                >
                  {event.title}
                </div>
              ))}
              {dayEvents.length > 3 && (
                <div className="calendar-more">
                  +{dayEvents.length - 3} more
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
