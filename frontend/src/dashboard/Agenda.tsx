import { useEffect, useState } from 'react';
import { format, isToday, isTomorrow, isPast, parseISO } from 'date-fns';
import { eventsApi, Event } from '../api/events';

interface AgendaProps {
  className?: string;
}

export const Agenda: React.FC<AgendaProps> = ({ className = '' }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const now = new Date();
        const sevenDaysLater = new Date();
        sevenDaysLater.setDate(sevenDaysLater.getDate() + 7);
        
        const data = await eventsApi.list(
          now.toISOString(),
          sevenDaysLater.toISOString()
        );
        setEvents(data);
      } catch (err) {
        console.error('Failed to load events:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const formatEventDate = (dateString: string) => {
    const date = parseISO(dateString);
    if (isToday(date)) return 'Today';
    if (isTomorrow(date)) return 'Tomorrow';
    return format(date, 'EEEE, d MMMM');
  };

  const formatEventTime = (dateString: string, allDay: boolean) => {
    if (allDay) return 'All day';
    return format(parseISO(dateString), 'HH:mm');
  };

  if (loading) {
    return <div className={`agenda loading ${className}`}>Loading agenda...</div>;
  }

  if (events.length === 0) {
    return <div className={`agenda empty ${className}`}>No events in the next 7 days</div>;
  }

  return (
    <div className={`agenda ${className}`}>
      <h2 className="agenda-title">Next 7 Days</h2>
      <div className="agenda-list">
        {events.map((event) => (
          <div
            key={event.id}
            className="agenda-item"
            style={{
              borderLeftColor: event.category?.colour || '#4A90E2'
            }}
          >
            <div className="agenda-date">{formatEventDate(event.start_datetime)}</div>
            <div className="agenda-time">{formatEventTime(event.start_datetime, event.all_day)}</div>
            <div className="agenda-title">{event.title}</div>
            {event.category && (
              <div
                className="agenda-category"
                style={{ backgroundColor: event.category.colour }}
              >
                {event.category.name}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
