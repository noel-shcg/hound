import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel

from ..core.config import settings


class BusService:
    """Service for fetching bus departures from Bustimes.org."""
    
    BASE_URL = "https://bustimes.org/stops"
    
    def __init__(self):
        self._cache: Dict[str, List[Dict]] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self._client.aclose()
    
    async def get_departures(
        self,
        atco_code: str,
        use_cache: bool = True
    ) -> List[Dict]:
        """Get upcoming departures for a bus stop."""
        # Check cache
        if use_cache and atco_code in self._cache and atco_code in self._cache_time:
            cache_age = datetime.utcnow() - self._cache_time[atco_code]
            if cache_age < timedelta(seconds=settings.bus_refresh_interval):
                return self._cache[atco_code]
        
        try:
            url = f"{self.BASE_URL}/{atco_code}/times.json"
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()
            
            departures = []
            now = datetime.utcnow()
            
            # Parse the response structure
            # The actual structure needs to be verified against the live API
            if isinstance(data, dict):
                # Try to find departures in the response
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                departure = self._parse_departure(item, now)
                                if departure:
                                    departures.append(departure)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        departure = self._parse_departure(item, now)
                        if departure:
                            departures.append(departure)
            
            # Sort by scheduled time
            departures.sort(key=lambda x: x.get("scheduled_time", ""))
            
            # Keep only the next 5
            departures = departures[:5]
            
            # Update cache
            self._cache[atco_code] = departures
            self._cache_time[atco_code] = datetime.utcnow()
            
            return departures
        except Exception as e:
            print(f"Error fetching bus departures for {atco_code}: {e}")
            # Return stale cached data if available
            if atco_code in self._cache:
                return self._cache[atco_code]
            
            return []
    
    def _parse_departure(self, item: Dict, now: datetime) -> Optional[Dict]:
        """Parse a single departure from the API response."""
        try:
            # The actual field names need to be verified against the live API
            # Common field names might include: time, aimed_departure_time, destination, line, route
            scheduled_time = item.get("time") or item.get("aimed_departure_time") or item.get("scheduled")
            destination = item.get("destination") or item.get("headsign")
            route = item.get("line") or item.get("route") or item.get("service")
            
            if not scheduled_time:
                return None
            
            # Parse the time and calculate countdown
            # The time format needs to be verified
            try:
                # Assume time is in HH:MM format
                if ":" in str(scheduled_time):
                    time_parts = str(scheduled_time).split(":")
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    
                    # Create datetime for today
                    departure_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # If the time has passed today, assume it's tomorrow
                    if departure_dt < now:
                        departure_dt += timedelta(days=1)
                    
                    countdown = int((departure_dt - now).total_seconds() / 60)
                    
                    # Only include if countdown is reasonable (not negative or too far in future)
                    if countdown < 0 or countdown > 1440:  # More than 24 hours
                        return None
                    
                    return {
                        "route": route,
                        "destination": destination,
                        "scheduled_time": f"{hour:02d}:{minute:02d}",
                        "countdown_minutes": countdown,
                        "status": "scheduled"
                    }
            except Exception:
                pass
            
            return None
        except Exception as e:
            print(f"Error parsing departure: {e}")
            return None
    
    async def get_stop_name(self, atco_code: str) -> Optional[str]:
        """Get the official name of a bus stop."""
        try:
            url = f"{self.BASE_URL}/{atco_code}/times.json"
            response = await self._client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Try to extract stop name from response
            if isinstance(data, dict):
                return data.get("name") or data.get("stop_name")
            
            return None
        except Exception as e:
            print(f"Error fetching stop name for {atco_code}: {e}")
            return None


# Singleton instance
bus_service = BusService()
