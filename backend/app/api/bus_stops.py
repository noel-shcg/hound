from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.bus_stop import BusStop
from ..schemas.bus_stop import BusStopCreate, BusStopUpdate, BusStopResponse, BusDeparture

router = APIRouter()


@router.get("/", response_model=List[BusStopResponse])
async def list_bus_stops(db: Session = Depends(get_db)):
    """List all bus stops."""
    stops = db.query(BusStop).order_by(BusStop.display_order, BusStop.id).all()
    return stops


@router.get("/{stop_id}", response_model=BusStopResponse)
async def get_bus_stop(stop_id: int, db: Session = Depends(get_db)):
    """Get a specific bus stop."""
    stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Bus stop not found")
    return stop


@router.post("/", response_model=BusStopResponse)
async def create_bus_stop(stop_data: BusStopCreate, db: Session = Depends(get_db)):
    """Create a new bus stop."""
    existing = db.query(BusStop).filter(BusStop.atco_code == stop_data.atco_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="ATCO code already exists")
    
    stop = BusStop(**stop_data.model_dump())
    db.add(stop)
    db.commit()
    db.refresh(stop)
    return stop


@router.put("/{stop_id}", response_model=BusStopResponse)
async def update_bus_stop(stop_id: int, stop_data: BusStopUpdate, db: Session = Depends(get_db)):
    """Update a bus stop."""
    stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Bus stop not found")
    
    update_data = stop_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stop, field, value)
    
    db.commit()
    db.refresh(stop)
    return stop


@router.delete("/{stop_id}")
async def delete_bus_stop(stop_id: int, db: Session = Depends(get_db)):
    """Delete a bus stop."""
    stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Bus stop not found")
    
    db.delete(stop)
    db.commit()
    return {"message": "Bus stop deleted"}


@router.get("/{stop_id}/departures", response_model=List[BusDeparture])
async def get_bus_departures(stop_id: int, db: Session = Depends(get_db)):
    """Get upcoming departures for a bus stop."""
    stop = db.query(BusStop).filter(BusStop.id == stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Bus stop not found")
    
    # This will be implemented by the bus service
    # For now, return empty list
    return []
