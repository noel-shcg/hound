from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class WeatherLocation(Base):
    __tablename__ = "weather_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
