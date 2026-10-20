from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict

from ..core.database import get_db
from ..models.system_status import SystemStatus
from ..schemas.system import SystemStatusResponse, HealthCheckResponse
from ..services.update_service import update_service

router = APIRouter()


@router.get("/status", response_model=Dict[str, SystemStatusResponse])
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status for all components."""
    statuses = db.query(SystemStatus).all()
    return {s.component: SystemStatusResponse(
        component=s.component,
        status=s.status,
        last_check=s.last_check,
        message=s.message,
        metadata=eval(s.metadata) if s.metadata else None
    ) for s in statuses}


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check."""
    components = {}
    
    # Check database
    try:
        db.execute("SELECT 1")
        components["database"] = SystemStatusResponse(
            component="database",
            status="healthy",
            last_check=datetime.utcnow(),
            message="Database connection successful"
        )
    except Exception as e:
        components["database"] = SystemStatusResponse(
            component="database",
            status="unhealthy",
            last_check=datetime.utcnow(),
            message=str(e)
        )
    
    # Check other components would be added here
    components["application"] = SystemStatusResponse(
        component="application",
        status="healthy",
        last_check=datetime.utcnow(),
        message="Application running"
    )
    
    overall_status = "healthy" if all(c.status == "healthy" for c in components.values()) else "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        version="0.1.0",
        components=components
    )


@router.post("/status/{component}")
async def update_component_status(
    component: str,
    status: str,
    message: str = None,
    metadata: Dict = None,
    db: Session = Depends(get_db)
):
    """Update the status of a component (for internal use)."""
    existing = db.query(SystemStatus).filter(SystemStatus.component == component).first()
    
    metadata_str = str(metadata) if metadata else None
    
    if existing:
        existing.status = status
        existing.last_check = datetime.utcnow()
        existing.message = message
        existing.metadata = metadata_str
    else:
        existing = SystemStatus(
            component=component,
            status=status,
            last_check=datetime.utcnow(),
            message=message,
            metadata=metadata_str
        )
        db.add(existing)
    
    db.commit()
    return {"message": "Status updated"}


@router.get("/updates/status")
async def get_update_status():
    """Get current update status."""
    return update_service.get_update_status()


@router.post("/updates/check")
async def check_for_updates():
    """Check for available updates."""
    return update_service.check_for_updates()


@router.post("/updates/apply")
async def apply_update():
    """Apply available updates."""
    return update_service.apply_update()
