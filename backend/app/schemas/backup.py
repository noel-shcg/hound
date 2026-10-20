from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BackupCreate(BaseModel):
    filename: str
    file_path: str
    file_size: int
    version: str
    is_manual: bool = False


class BackupResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_size: int
    version: str
    is_manual: bool
    success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
