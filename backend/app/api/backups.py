from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil
import tarfile
from datetime import datetime
import os

from ..core.database import get_db
from ..core.config import settings
from ..models.backup import Backup
from ..schemas.backup import BackupResponse

router = APIRouter()


@router.get("/", response_model=List[BackupResponse])
async def list_backups(db: Session = Depends(get_db)):
    """List all backups."""
    backups = db.query(Backup).order_by(Backup.created_at.desc()).all()
    return backups


@router.post("/create", response_model=BackupResponse)
async def create_backup(db: Session = Depends(get_db)):
    """Create a new backup."""
    # Ensure backup directory exists
    backup_dir = Path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"hound_backup_{timestamp}.tar.gz"
    file_path = backup_dir / filename
    
    try:
        # Create backup archive
        with tarfile.open(file_path, "w:gz") as tar:
            # Add database
            db_path = Path(settings.database_path)
            if db_path.exists():
                tar.add(db_path, arcname="hound.db")
            
            # Add photos
            photo_dir = Path(settings.photo_dir)
            if photo_dir.exists():
                tar.add(photo_dir, arcname="photos")
        
        file_size = file_path.stat().st_size
        
        # Create database record
        backup = Backup(
            filename=filename,
            file_path=str(file_path),
            file_size=file_size,
            version="0.1.0",
            is_manual=True,
            success=True
        )
        db.add(backup)
        db.commit()
        db.refresh(backup)
        
        return backup
    except Exception as e:
        # Clean up failed backup
        if file_path.exists():
            file_path.unlink()
        
        backup = Backup(
            filename=filename,
            file_path=str(file_path),
            file_size=0,
            version="0.1.0",
            is_manual=True,
            success=False,
            error_message=str(e)
        )
        db.add(backup)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/restore/{backup_id}")
async def restore_backup(backup_id: int, db: Session = Depends(get_db)):
    """Restore from a backup."""
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    if not backup.success:
        raise HTTPException(status_code=400, detail="Cannot restore from failed backup")
    
    backup_path = Path(backup.file_path)
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    try:
        # Create a safety backup of current state first
        safety_timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safety_filename = f"hound_safety_{safety_timestamp}.tar.gz"
        safety_path = Path(settings.backup_dir) / safety_filename
        
        with tarfile.open(safety_path, "w:gz") as tar:
            db_path = Path(settings.database_path)
            if db_path.exists():
                tar.add(db_path, arcname="hound.db")
            photo_dir = Path(settings.photo_dir)
            if photo_dir.exists():
                tar.add(photo_dir, arcname="photos")
        
        # Extract backup to temporary location first
        temp_dir = Path(settings.backup_dir) / "temp_restore"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        with tarfile.open(backup_path, "r:gz") as tar:
            # Validate archive contents
            for member in tar.getmembers():
                # Prevent path traversal
                if ".." in member.name or member.name.startswith("/"):
                    raise HTTPException(status_code=400, detail="Invalid backup archive")
            
            tar.extractall(path=temp_dir)
        
        # Move files to actual locations
        temp_db = temp_dir / "hound.db"
        if temp_db.exists():
            shutil.copy2(temp_db, settings.database_path)
        
        temp_photos = temp_dir / "photos"
        if temp_photos.exists():
            # Clear existing photos
            existing_photo_dir = Path(settings.photo_dir)
            if existing_photo_dir.exists():
                shutil.rmtree(existing_photo_dir)
            shutil.copytree(temp_photos, existing_photo_dir)
        
        # Clean up temp directory
        shutil.rmtree(temp_dir)
        
        return {"message": "Backup restored successfully", "safety_backup": safety_filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.delete("/{backup_id}")
async def delete_backup(backup_id: int, db: Session = Depends(get_db)):
    """Delete a backup."""
    backup = db.query(Backup).filter(Backup.id == backup_id).first()
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    # Delete file
    file_path = Path(backup.file_path)
    if file_path.exists():
        file_path.unlink()
    
    db.delete(backup)
    db.commit()
    return {"message": "Backup deleted"}
