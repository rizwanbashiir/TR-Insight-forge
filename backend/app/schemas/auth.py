from pydantic import BaseModel, EmailStr, Field, AliasChoices, field_validator, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional

class UserRole(str, Enum):
    admin   = "admin"
    analyst = "analyst"
    viewer  = "viewer"

# ── Request schemas (what client sends) ──
class RegisterRequest(BaseModel):
    email:      EmailStr
    password:   str
    name:       Optional[str] = None
    first_name: Optional[str] = Field(None, validation_alias=AliasChoices("first_name", "firstName"))
    last_name:  Optional[str] = Field(None, validation_alias=AliasChoices("last_name", "lastName"))
    role:       UserRole = UserRole.analyst
    org_name:   Optional[str] = Field(None, validation_alias=AliasChoices("org_name", "orgName", "organization_name"))
    industry:   Optional[str] = None
    team_size:  Optional[str] = Field(None, validation_alias=AliasChoices("team_size", "teamSize"))
    plan:       Optional[str] = None

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

# ── Response schemas (what server returns) ──
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         Optional[str] = None
    name:       str
    first_name: Optional[str] = None
    last_name:  Optional[str] = None
    email:      str
    role:       UserRole
    is_active:  bool
    org_name:   Optional[str] = None
    industry:   Optional[str] = None
    team_size:  Optional[str] = None
    plan:       Optional[str] = None
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def serialize_id(cls, v):
        return str(v) if v is not None else None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type:   str = "bearer"
    user:         UserResponse

class VerifyRequest(BaseModel):
    email: EmailStr
    code:  str

class GoogleLoginRequest(BaseModel):
    token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class SetPasswordRequest(BaseModel):
    token: str
    new_password: str