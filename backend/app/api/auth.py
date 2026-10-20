from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..core.database import get_db
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    check_login_throttling,
    record_failed_attempt,
    reset_failed_attempts,
)
from ..models.credential import Credential
from ..schemas.credential import CredentialCreate, CredentialResponse

router = APIRouter()


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/setup", response_model=CredentialResponse)
async def setup_credential(
    credential_data: CredentialCreate,
    db: Session = Depends(get_db)
):
    """Set up the initial management credential. Can only be called once."""
    existing = db.query(Credential).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credential already exists. Use the change endpoint instead.",
        )
    
    credential = Credential(
        hashed_password=get_password_hash(credential_data.password)
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    
    return credential


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate and receive an access token."""
    credential = await check_login_throttling(db)
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No credential configured. Use /setup first.",
        )
    
    if not verify_password(login_data.password, credential.hashed_password):
        record_failed_attempt(db, credential)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )
    
    reset_failed_attempts(db, credential)
    
    access_token = create_access_token(data={"sub": str(credential.id)})
    return LoginResponse(access_token=access_token)


@router.post("/change-password")
async def change_password(
    new_password: str,
    current_credential: Credential = Depends(lambda: None),  # Will be replaced with actual auth
    db: Session = Depends(get_db)
):
    """Change the management password."""
    # This will require authentication in the actual implementation
    credential = db.query(Credential).first()
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No credential configured",
        )
    
    credential.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
