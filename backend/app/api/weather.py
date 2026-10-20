from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.weather_location import WeatherLocation
from ..schemas.weather import WeatherLocationCreate, WeatherLocationResponse, WeatherData, WeatherForecast

router = APIRouter()


@router.get("/location", response_model=WeatherLocationResponse)
async def get_weather_location(db: Session = Depends(get_db)):
    """Get the configured weather location."""
    location = db.query(WeatherLocation).first()
    if not location:
        raise HTTPException(status_code=404, detail="Weather location not configured")
    return location


@router.post("/location", response_model=WeatherLocationResponse)
async def set_weather_location(location_data: WeatherLocationCreate, db: Session = Depends(get_db)):
    """Set the weather location."""
    # Remove existing location if any
    db.query(WeatherLocation).delete()
    
    location = WeatherLocation(**location_data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.get("/current", response_model=WeatherData)
async def get_current_weather(db: Session = Depends(get_db)):
    """Get current weather data."""
    # This will be implemented by the weather service
    # For now, return empty data
    return WeatherData()


@router.get("/forecast", response_model=List[WeatherForecast])
async def get_weather_forecast(db: Session = Depends(get_db)):
    """Get weather forecast."""
    # This will be implemented by the weather service
    # For now, return empty list
    return []


@router.get("/search")
async def search_weather_location(query: str):
    """Search for a weather location by name."""
    # This will use Open-Meteo geocoding API
    # For now, return empty results
    return {"results": []}
