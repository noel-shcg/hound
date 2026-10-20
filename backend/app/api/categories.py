from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..models.event_category import EventCategory
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all event categories."""
    categories = db.query(EventCategory).all()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category."""
    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    existing = db.query(EventCategory).filter(EventCategory.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    category = EventCategory(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    """Update a category."""
    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if any events use this category
    from ..models.event import Event
    events_using = db.query(Event).filter(Event.category_id == category_id).count()
    if events_using > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category: {events_using} events reference it"
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}
