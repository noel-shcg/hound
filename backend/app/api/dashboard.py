from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional

from ..core.database import get_db
from ..models.event import Event
from ..models.bus_stop import BusStop
from ..models.weather_location import WeatherLocation
from ..schemas.bus_stop import BusDeparture
from ..schemas.weather import WeatherData, WeatherForecast

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get aggregated data for the dashboard."""
    today = date.today()
    seven_days_later = today + timedelta(days=7)
    
    # Get events for the next 7 days
    events = db.query(Event).filter(
        Event.start_datetime >= datetime.combine(today, datetime.min.time()),
        Event.start_datetime <= datetime.combine(seven_days_later, datetime.max.time())
    ).order_by(Event.start_datetime).all()
    
    # Get enabled bus stops
    bus_stops = db.query(BusStop).filter(BusStop.enabled == True).order_by(BusStop.display_order).all()
    
    # Get weather location
    weather_location = db.query(WeatherLocation).first()
    
    return {
        "date": today.isoformat(),
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_datetime": e.start_datetime.isoformat(),
                "end_datetime": e.end_datetime.isoformat() if e.end_datetime else None,
                "all_day": e.all_day,
                "category_id": e.category_id,
                "category": {
                    "id": e.category.id,
                    "name": e.category.name,
                    "colour": e.category.colour
                } if e.category else None
            }
            for e in events
        ],
        "bus_stops": [
            {
                "id": s.id,
                "atco_code": s.atco_code,
                "custom_label": s.custom_label,
                "official_name": s.official_name
            }
            for s in bus_stops
        ],
        "weather_location": {
            "id": weather_location.id,
            "name": weather_location.name,
            "latitude": weather_location.latitude,
            "longitude": weather_location.longitude
        } if weather_location else None
    }


@router.get("/bus-departures")
async def get_all_bus_departures(db: Session = Depends(get_db)):
    """Get bus departures for all enabled stops."""
    # This will be implemented by the bus service
    # For now, return empty data
    bus_stops = db.query(BusStop).filter(BusStop.enabled == True).all()
    
    return {
        "stops": [
            {
                "id": s.id,
                "atco_code": s.atco_code,
                "custom_label": s.custom_label,
                "departures": []
            }
            for s in bus_stops
        ],
        "last_updated": None
    }


@router.get("/weather/current", response_model=WeatherData)
async def get_dashboard_weather(db: Session = Depends(get_db)):
    """Get current weather for dashboard."""
    # This will be implemented by the weather service
    return WeatherData()


@router.get("/weather/forecast")
async def get_dashboard_forecast(db: Session = Depends(get_db)):
    """Get weather forecast for dashboard."""
    # This will be implemented by the weather service
    return {"forecast": []}


@router.get("/calendar/month")
async def get_calendar_month(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get events for a specific month."""
    from calendar import monthrange
    
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    
    events = db.query(Event).filter(
        Event.start_datetime >= datetime.combine(first_day, datetime.min.time()),
        Event.start_datetime <= datetime.combine(last_day, datetime.max.time())
    ).all()
    
    return {
        "year": year,
        "month": month,
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "start_datetime": e.start_datetime.isoformat(),
                "all_day": e.all_day,
                "category_id": e.category_id,
                "category": {
                    "id": e.category.id,
                    "name": e.category.name,
                    "colour": e.category.colour
                } if e.category else None
            }
            for e in events
        ]
    }
