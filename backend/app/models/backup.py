from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class Backup(Base):
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    version = Column(String, nullable=False)
    is_manual = Column(Boolean, default=False)
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
