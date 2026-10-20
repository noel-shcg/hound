import { useEffect, useState } from 'react';
import { weatherApi, WeatherData } from '../api/weather';

interface WeatherDisplayProps {
  className?: string;
}

export const WeatherDisplay: React.FC<WeatherDisplayProps> = ({ className = '' }) => {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        setLoading(true);
        const data = await weatherApi.getCurrent();
        setWeather(data);
        setError(null);
      } catch (err) {
        setError('Failed to load weather');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWeather();
    const interval = setInterval(fetchWeather, 900000); // Refresh every 15 minutes

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className={`weather-display loading ${className}`}>Loading weather...</div>;
  }

  if (error || !weather) {
    return <div className={`weather-display error ${className}`}>Weather unavailable</div>;
  }

  if (weather.is_stale) {
    return (
      <div className={`weather-display stale ${className}`}>
        <div className="weather-warning">Weather data is stale</div>
        {weather.temperature && <div className="weather-temp">{Math.round(weather.temperature)}°C</div>}
      </div>
    );
  }

  return (
    <div className={`weather-display ${className}`}>
      <div className="weather-main">
        {weather.temperature && (
          <div className="weather-temp">{Math.round(weather.temperature)}°C</div>
        )}
        {weather.condition && (
          <div className="weather-condition">{weather.condition}</div>
        )}
      </div>
      {weather.feels_like && (
        <div className="weather-details">
          Feels like {Math.round(weather.feels_like)}°C
        </div>
      )}
      {weather.last_updated && (
        <div className="weather-updated">
          Updated: {new Date(weather.last_updated).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};
