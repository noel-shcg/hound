from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.settings import Setting
from ..schemas.settings import SettingCreate, SettingUpdate, SettingResponse

router = APIRouter()


@router.get("/", response_model=List[SettingResponse])
async def list_settings(db: Session = Depends(get_db)):
    """List all settings."""
    settings = db.query(Setting).all()
    return settings


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(key: str, db: Session = Depends(get_db)):
    """Get a specific setting by key."""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.post("/", response_model=SettingResponse)
async def create_setting(setting_data: SettingCreate, db: Session = Depends(get_db)):
    """Create a new setting."""
    existing = db.query(Setting).filter(Setting.key == setting_data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Setting key already exists")
    
    setting = Setting(**setting_data.model_dump())
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(key: str, setting_data: SettingUpdate, db: Session = Depends(get_db)):
    """Update a setting."""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.value = setting_data.value
    db.commit()
    db.refresh(setting)
    return setting


@router.delete("/{key}")
async def delete_setting(key: str, db: Session = Depends(get_db)):
    """Delete a setting."""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(setting)
    db.commit()
    return {"message": "Setting deleted"}
