import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { enGB } from 'date-fns/locale';

interface ClockProps {
  className?: string;
}

export const Clock: React.FC<ClockProps> = ({ className = '' }) => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const timeString = format(time, 'HH:mm', { locale: enGB });
  const dateString = format(time, 'd MMMM yyyy', { locale: enGB });
  const dayString = format(time, 'EEEE', { locale: enGB });

  return (
    <div className={`clock ${className}`}>
      <div className="clock-time">{timeString}</div>
      <div className="clock-date">{dayString}, {dateString}</div>
    </div>
  );
};
