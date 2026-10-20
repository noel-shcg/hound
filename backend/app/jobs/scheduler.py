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
from ..services.update_service import update_service


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


async def check_updates_job():
    """Background job to check for and apply automatic updates."""
    try:
        # Check if auto-update is enabled
        from ..core.config import settings as config_settings
        if not config_settings.auto_update_enabled:
            return
        
        # Check for updates
        status = update_service.check_for_updates()
        
        if status.get("available"):
            print("Updates available, applying...")
            result = update_service.apply_update()
            
            if result.get("success"):
                print("Update applied successfully")
            else:
                print(f"Update failed: {result.get('error')}")
        
        # Update system status
        db = SessionLocal()
        try:
            update_status = update_service.get_update_status()
            sys_status = db.query(SystemStatus).filter(SystemStatus.component == "updates").first()
            if sys_status:
                sys_status.status = "healthy" if not update_status.get("update_available") else "update_available"
                sys_status.last_check = datetime.utcnow()
                sys_status.message = f"Updates available: {update_status.get('update_available')}"
                sys_status.metadata = str(update_status)
            else:
                sys_status = SystemStatus(
                    component="updates",
                    status="healthy" if not update_status.get("update_available") else "update_available",
                    last_check=datetime.utcnow(),
                    message=f"Updates available: {update_status.get('update_available')}",
                    metadata=str(update_status)
                )
                db.add(sys_status)
            db.commit()
        except Exception as e:
            print(f"Error updating system status: {e}")
        finally:
            db.close()
    
    except Exception as e:
        print(f"Error in update check job: {e}")


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
    
    # Update check job (run daily)
    scheduler.add_job(
        check_updates_job,
        trigger=IntervalTrigger(seconds=settings.update_check_interval),
        id="check_updates",
        name="Check for updates",
        replace_existing=True
    )
    
    scheduler.start()
    print("Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    print("Background scheduler stopped")
