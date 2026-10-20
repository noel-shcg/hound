from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class BusStop(Base):
    __tablename__ = "bus_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    atco_code = Column(String, unique=True, nullable=False, index=True)
    custom_label = Column(String, nullable=False)
    official_name = Column(String, nullable=True)
    enabled = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
