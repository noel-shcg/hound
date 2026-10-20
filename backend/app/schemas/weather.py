from pydantic import BaseModel
from typing import Optional, List


class WeatherLocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float


class WeatherLocationResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class WeatherData(BaseModel):
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    condition: Optional[str] = None
    icon: Optional[str] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    last_updated: Optional[str] = None
    is_stale: bool = False


class WeatherForecast(BaseModel):
    date: str
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    condition: Optional[str] = None
    icon: Optional[str] = None
