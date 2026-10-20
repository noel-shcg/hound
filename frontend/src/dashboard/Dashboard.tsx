import { useState, useEffect } from 'react';
import { useTheme } from '../hooks/useTheme';
import { Clock } from '../components/Clock';
import { WeatherDisplay } from '../components/WeatherDisplay';
import { BusDisplay } from '../components/BusDisplay';
import { Calendar } from './Calendar';
import { Agenda } from './Agenda';
import { Screensaver } from '../components/Screensaver';

export const Dashboard: React.FC = () => {
  const { colors, designTokens } = useTheme();
  const [screensaverActive, setScreensaverActive] = useState(false);
  const [lastInteraction, setLastInteraction] = useState(Date.now());

  useEffect(() => {
    const handleInteraction = () => {
      setLastInteraction(Date.now());
      if (screensaverActive) {
        setScreensaverActive(false);
      }
    };

    window.addEventListener('click', handleInteraction);
    window.addEventListener('touchstart', handleInteraction);
    window.addEventListener('keydown', handleInteraction);

    return () => {
      window.removeEventListener('click', handleInteraction);
      window.removeEventListener('touchstart', handleInteraction);
      window.removeEventListener('keydown', handleInteraction);
    };
  }, [screensaverActive]);

  useEffect(() => {
    const checkInactivity = () => {
      const inactiveTime = Date.now() - lastInteraction;
      if (inactiveTime >= 60000) { // 1 minute
        setScreensaverActive(true);
      }
    };

    const interval = setInterval(checkInactivity, 1000);
    return () => clearInterval(interval);
  }, [lastInteraction]);

  if (screensaverActive) {
    return (
      <Screensaver
        isActive={true}
        onWake={() => setScreensaverActive(false)}
      />
    );
  }

  return (
    <div
      className="dashboard"
      style={{
        '--background': colors.background,
        '--surface': colors.surface,
        '--text': colors.text,
        '--text-secondary': colors.textSecondary,
        '--border': colors.border,
        '--primary': colors.primary,
        '--secondary': colors.secondary,
        fontFamily: designTokens.typography.fontFamily,
      } as React.CSSProperties}
    >
      <div className="dashboard-grid">
        {/* Clock and Date */}
        <div className="dashboard-card clock-card">
          <Clock />
        </div>

        {/* Weather */}
        <div className="dashboard-card weather-card">
          <WeatherDisplay />
        </div>

        {/* Bus Departures */}
        <div className="dashboard-card bus-card">
          <BusDisplay />
        </div>

        {/* Calendar */}
        <div className="dashboard-card calendar-card">
          <Calendar />
        </div>

        {/* Agenda */}
        <div className="dashboard-card agenda-card">
          <Agenda />
        </div>
      </div>
    </div>
  );
};
