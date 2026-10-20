import { useEffect, useState } from 'react';
import { busApi } from '../api/bus';
import type { BusStop, BusDeparture } from '../api/bus';

interface BusDisplayProps {
  className?: string;
}

export const BusDisplay: React.FC<BusDisplayProps> = ({ className = '' }) => {
  const [stops, setStops] = useState<BusStop[]>([]);
  const [departures, setDepartures] = useState<Record<number, BusDeparture[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBusData = async () => {
      try {
        setLoading(true);
        const stopsData = await busApi.list();
        setStops(stopsData);

        // Fetch departures for each stop
        const departuresData: Record<number, BusDeparture[]> = {};
        for (const stop of stopsData) {
          if (stop.enabled) {
            try {
              const stopDepartures = await busApi.getDepartures(stop.id);
              departuresData[stop.id] = stopDepartures;
            } catch (err) {
              console.error(`Failed to fetch departures for stop ${stop.id}:`, err);
              departuresData[stop.id] = [];
            }
          }
        }
        setDepartures(departuresData);
        setError(null);
      } catch (err) {
        setError('Failed to load bus information');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBusData();
    const interval = setInterval(fetchBusData, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className={`bus-display loading ${className}`}>Loading bus information...</div>;
  }

  if (error) {
    return <div className={`bus-display error ${className}`}>Bus information unavailable</div>;
  }

  if (stops.length === 0) {
    return <div className={`bus-display empty ${className}`}>No bus stops configured</div>;
  }

  return (
    <div className={`bus-display ${className}`}>
      {stops.map((stop) => {
        if (!stop.enabled) return null;
        const stopDepartures = departures[stop.id] || [];
        
        return (
          <div key={stop.id} className="bus-stop">
            <div className="bus-stop-name">
              {stop.custom_label}
              {stop.official_name && <span className="bus-stop-official"> ({stop.official_name})</span>}
            </div>
            <div className="bus-departures">
              {stopDepartures.length === 0 ? (
                <div className="no-departures">No upcoming departures</div>
              ) : (
                stopDepartures.map((dep, idx) => (
                  <div key={idx} className="bus-departure">
                    {dep.route && <span className="departure-route">{dep.route}</span>}
                    {dep.destination && <span className="departure-destination">{dep.destination}</span>}
                    {dep.scheduled_time && (
                      <span className="departure-time">{dep.scheduled_time}</span>
                    )}
                    {dep.countdown_minutes !== undefined && (
                      <span className="departure-countdown">{dep.countdown_minutes} min</span>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
