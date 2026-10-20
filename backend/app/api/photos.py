from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import uuid
import imghdr
from PIL import Image
import aiofiles

from ..core.database import get_db
from ..core.config import settings
from ..models.photo import Photo
from ..schemas.photo import PhotoResponse

router = APIRouter()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.get("/", response_model=List[PhotoResponse])
async def list_photos(db: Session = Depends(get_db)):
    """List all photos."""
    photos = db.query(Photo).order_by(Photo.created_at.desc()).all()
    return photos


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """Get a specific photo."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo


@router.post("/upload", response_model=PhotoResponse)
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a new photo."""
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Validate it's actually an image
    file_type = imghdr.what(None, content)
    if not file_type:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Generate safe filename
    file_extension = Path(file.filename).suffix or f".{file_type}"
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = Path(settings.photo_dir) / safe_filename
    
    # Save file
    Path(settings.photo_dir).mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Get image dimensions
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except Exception:
        width, height = None, None
    
    # Create database record
    photo = Photo(
        filename=safe_filename,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=len(content),
        mime_type=file.content_type,
        width=width,
        height=height
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    
    return photo


@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """Delete a photo."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete file
    file_path = Path(photo.file_path)
    if file_path.exists():
        file_path.unlink()
    
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted"}
