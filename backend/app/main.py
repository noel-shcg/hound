from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from .core.database import engine, get_db, Base
from .core.config import settings
from .api import auth, settings, bus_stops, weather, events, categories, reminders, photos, backups, system, dashboard
from .jobs.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler(settings)
    yield
    # Shutdown
    stop_scheduler()


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hound API",
    description="Household dashboard backend API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to LAN
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(bus_stops.router, prefix="/api/bus-stops", tags=["Bus Stops"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Reminders"])
app.include_router(photos.router, prefix="/api/photos", tags=["Photos"])
app.include_router(backups.router, prefix="/api/backups", tags=["Backups"])
app.include_router(system.router, prefix="/api/system", tags=["System"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# Serve uploaded photos
photo_dir = Path(settings.photo_dir)
photo_dir.mkdir(parents=True, exist_ok=True)
app.mount("/photos", StaticFiles(directory=str(photo_dir)), name="photos")


@app.get("/")
async def root():
    return {"message": "Hound API", "version": "0.1.0"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Basic health check endpoint."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
