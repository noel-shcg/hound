from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class SystemStatus(Base):
    __tablename__ = "system_status"
    
    id = Column(Integer, primary_key=True, index=True)
    component = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)  # healthy, unhealthy, unknown
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    message = Column(String, nullable=True)
    metadata = Column(String, nullable=True)  # JSON string for additional info
