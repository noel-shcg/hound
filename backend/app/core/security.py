from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from ..models.credential import Credential

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Credential:
    """Get the current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    credential = db.query(Credential).first()
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credentials configured",
        )
    
    return credential


async def check_login_throttling(db: Session) -> Optional[Credential]:
    """Check if login attempts should be throttled."""
    credential = db.query(Credential).first()
    if not credential:
        return None
    
    if credential.failed_attempts >= 5:
        if credential.last_failed_attempt:
            time_since_failure = datetime.utcnow() - credential.last_failed_attempt
            if time_since_failure < timedelta(minutes=15):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed attempts. Please try again later.",
                )
    
    return credential


def record_failed_attempt(db: Session, credential: Credential):
    """Record a failed login attempt."""
    credential.failed_attempts += 1
    credential.last_failed_attempt = datetime.utcnow()
    db.commit()


def reset_failed_attempts(db: Session, credential: Credential):
    """Reset failed login attempts after successful login."""
    credential.failed_attempts = 0
    credential.last_failed_attempt = None
    db.commit()
