from pydantic import BaseModel


class CredentialCreate(BaseModel):
    password: str


class CredentialResponse(BaseModel):
    id: int
    credential_type: str
    created_at: str

    class Config:
        from_attributes = True
