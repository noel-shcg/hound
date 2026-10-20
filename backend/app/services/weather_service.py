import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel

from ..core.config import settings


class WeatherCode:
    """Open-Meteo weather code mappings."""
    CODES = {
        0: {"description": "Clear sky", "icon": "clear"},
        1: {"description": "Mainly clear", "icon": "partly-cloudy"},
        2: {"description": "Partly cloudy", "icon": "partly-cloudy"},
        3: {"description": "Overcast", "icon": "cloudy"},
        45: {"description": "Fog", "icon": "fog"},
        48: {"description": "Depositing rime fog", "icon": "fog"},
        51: {"description": "Light drizzle", "icon": "rain"},
        53: {"description": "Moderate drizzle", "icon": "rain"},
        55: {"description": "Dense drizzle", "icon": "rain"},
        56: {"description": "Light freezing drizzle", "icon": "rain"},
        57: {"description": "Dense freezing drizzle", "icon": "rain"},
        61: {"description": "Slight rain", "icon": "rain"},
        63: {"description": "Moderate rain", "icon": "rain"},
        65: {"description": "Heavy rain", "icon": "rain"},
        66: {"description": "Light freezing rain", "icon": "rain"},
        67: {"description": "Heavy freezing rain", "icon": "rain"},
        71: {"description": "Slight snow fall", "icon": "snow"},
        73: {"description": "Moderate snow fall", "icon": "snow"},
        75: {"description": "Heavy snow fall", "icon": "snow"},
        77: {"description": "Snow grains", "icon": "snow"},
        80: {"description": "Slight rain showers", "icon": "rain"},
        81: {"description": "Moderate rain showers", "icon": "rain"},
        82: {"description": "Violent rain showers", "icon": "rain"},
        85: {"description": "Slight snow showers", "icon": "snow"},
        86: {"description": "Heavy snow showers", "icon": "snow"},
        95: {"description": "Thunderstorm", "icon": "thunder"},
        96: {"description": "Thunderstorm with slight hail", "icon": "thunder"},
        99: {"description": "Thunderstorm with heavy hail", "icon": "thunder"},
    }
    
    @classmethod
    def get_description(cls, code: int) -> str:
        return cls.CODES.get(code, {}).get("description", "Unknown")
    
    @classmethod
    def get_icon(cls, code: int) -> str:
        return cls.CODES.get(code, {}).get("icon", "unknown")


class WeatherService:
    """Service for fetching weather data from Open-Meteo."""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1"
    
    def __init__(self):
        self._cache: Optional[Dict] = None
        self._cache_time: Optional[datetime] = None
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self._client.aclose()
    
    async def search_location(self, query: str) -> List[Dict]:
        """Search for a location by name using geocoding API."""
        try:
            response = await self._client.get(
                f"{self.GEOCODING_URL}/search",
                params={"name": query, "count": 5, "language": "en", "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "results" in data:
                for result in data["results"]:
                    results.append({
                        "name": result.get("name"),
                        "latitude": result.get("latitude"),
                        "longitude": result.get("longitude"),
                        "country": result.get("country"),
                        "admin1": result.get("admin1")
                    })
            
            return results
        except Exception as e:
            print(f"Error searching location: {e}")
            return []
    
    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        use_cache: bool = True
    ) -> Dict:
        """Get current weather data."""
        # Check cache
        if use_cache and self._cache and self._cache_time:
            cache_age = datetime.utcnow() - self._cache_time
            if cache_age < timedelta(seconds=settings.weather_refresh_interval):
                return self._cache
        
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m,wind_direction_10m",
                    "timezone": "auto"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            weather_code = current.get("weather_code", 0)
            
            result = {
                "temperature": current.get("temperature_2m"),
                "feels_like": current.get("apparent_temperature"),
                "condition": WeatherCode.get_description(weather_code),
                "icon": WeatherCode.get_icon(weather_code),
                "humidity": current.get("relative_humidity_2m"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "is_day": current.get("is_day"),
                "precipitation": current.get("precipitation"),
                "last_updated": datetime.utcnow().isoformat(),
                "is_stale": False
            }
            
            # Update cache
            self._cache = result
            self._cache_time = datetime.utcnow()
            
            return result
        except Exception as e:
            print(f"Error fetching weather: {e}")
            # Return stale cached data if available
            if self._cache:
                self._cache["is_stale"] = True
                return self._cache
            
            return {
                "temperature": None,
                "feels_like": None,
                "condition": None,
                "icon": None,
                "last_updated": None,
                "is_stale": True,
                "error": str(e)
            }
    
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> List[Dict]:
        """Get weather forecast."""
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                    "timezone": "auto",
                    "forecast_days": days
                }
            )
            response.raise_for_status()
            data = response.json()
            
            daily = data.get("daily", {})
            forecast = []
            
            for i in range(len(daily.get("time", []))):
                weather_code = daily.get("weather_code", [0])[i]
                forecast.append({
                    "date": daily.get("time", [])[i],
                    "temperature_max": daily.get("temperature_2m_max", [])[i],
                    "temperature_min": daily.get("temperature_2m_min", [])[i],
                    "condition": WeatherCode.get_description(weather_code),
                    "icon": WeatherCode.get_icon(weather_code)
                })
            
            return forecast
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return []


# Singleton instance
weather_service = WeatherService()
