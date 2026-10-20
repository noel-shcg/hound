from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class SystemStatusResponse(BaseModel):
    component: str
    status: str
    last_check: Optional[datetime] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    components: Dict[str, SystemStatusResponse]
