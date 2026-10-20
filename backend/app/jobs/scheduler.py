from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from ..core.database import SessionLocal
from ..models.bus_stop import BusStop
from ..models.weather_location import WeatherLocation
from ..models.system_status import SystemStatus
from ..services.weather_service import weather_service
from ..services.bus_service import bus_service
from ..services.reminder_service import reminder_service


scheduler = AsyncIOScheduler()


async def refresh_weather_job():
    """Background job to refresh weather data."""
    db = SessionLocal()
    try:
        location = db.query(WeatherLocation).first()
        if not location:
            print("No weather location configured")
            return
        
        try:
            await weather_service.get_current_weather(
                location.latitude,
                location.longitude,
                use_cache=False
            )
            
            # Update system status
            status = db.query(SystemStatus).filter(SystemStatus.component == "weather").first()
            if status:
                status.status = "healthy"
                status.last_check = datetime.utcnow()
                status.message = "Weather data refreshed successfully"
            else:
                status = SystemStatus(
                    component="weather",
                    status="healthy",
                    last_check=datetime.utcnow(),
                    message="Weather data refreshed successfully"
                )
                db.add(status)
            
            db.commit()
            print(f"Weather refreshed for {location.name}")
        except Exception as e:
            print(f"Error refreshing weather: {e}")
            
            # Update system status
            status = db.query(SystemStatus).filter(SystemStatus.component == "weather").first()
            if status:
                status.status = "unhealthy"
                status.last_check = datetime.utcnow()
                status.message = str(e)
            else:
                status = SystemStatus(
                    component="weather",
                    status="unhealthy",
                    last_check=datetime.utcnow(),
                    message=str(e)
                )
                db.add(status)
            
            db.commit()
    finally:
        db.close()


async def refresh_bus_job():
    """Background job to refresh bus departure data."""
    db = SessionLocal()
    try:
        stops = db.query(BusStop).filter(BusStop.enabled == True).all()
        
        for stop in stops:
            try:
                await bus_service.get_departures(stop.atco_code, use_cache=False)
                print(f"Bus departures refreshed for {stop.custom_label}")
            except Exception as e:
                print(f"Error refreshing bus departures for {stop.atco_code}: {e}")
        
        # Update system status
        status = db.query(SystemStatus).filter(SystemStatus.component == "bus").first()
        if status:
            status.status = "healthy"
            status.last_check = datetime.utcnow()
            status.message = f"Refreshed {len(stops)} bus stops"
        else:
            status = SystemStatus(
                component="bus",
                status="healthy",
                last_check=datetime.utcnow(),
                message=f"Refreshed {len(stops)} bus stops"
            )
            db.add(status)
        
        db.commit()
    except Exception as e:
        print(f"Error in bus refresh job: {e}")
    finally:
        db.close()


async def evaluate_reminders_job():
    """Background job to evaluate and create reminders for recurring events."""
    db = SessionLocal()
    try:
        reminder_service.evaluate_recurring_reminders(db, days_ahead=7)
        print("Reminders evaluated")
        db.commit()
    except Exception as e:
        print(f"Error evaluating reminders: {e}")
    finally:
        db.close()


def start_scheduler(settings):
    """Start the background scheduler."""
    # Weather refresh job
    scheduler.add_job(
        refresh_weather_job,
        trigger=IntervalTrigger(seconds=settings.weather_refresh_interval),
        id="refresh_weather",
        name="Refresh weather data",
        replace_existing=True
    )
    
    # Bus refresh job
    scheduler.add_job(
        refresh_bus_job,
        trigger=IntervalTrigger(seconds=settings.bus_refresh_interval),
        id="refresh_bus",
        name="Refresh bus departures",
        replace_existing=True
    )
    
    # Reminder evaluation job (run every hour)
    scheduler.add_job(
        evaluate_reminders_job,
        trigger=IntervalTrigger(hours=1),
        id="evaluate_reminders",
        name="Evaluate recurring reminders",
        replace_existing=True
    )
    
    scheduler.start()
    print("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    print("Background scheduler stopped")
