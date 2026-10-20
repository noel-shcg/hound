from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class Credential(Base):
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    credential_type = Column(String, nullable=False, default="management_password")
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_failed_attempt = Column(DateTime(timezone=True), nullable=True)
    failed_attempts = Column(Integer, default=0)
