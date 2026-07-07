from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional

class UserRole(str, Enum):
    admin   = "admin"
    analyst = "analyst"
    viewer  = "viewer"

# ── Request schemas (what client sends) ──
class RegisterRequest(BaseModel):
    name:       Optional[str] = None
    first_name: Optional[str] = None
    last_name:  Optional[str] = None
    email:      EmailStr
    password:   str
    role:       UserRole = UserRole.analyst
    org_name:   Optional[str] = None
    industry:   Optional[str] = None
    team_size:  Optional[str] = None
    plan:       Optional[str] = None

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

# ── Response schemas (what server returns) ──
class UserResponse(BaseModel):
    id:         int
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

    class Config:
        from_attributes = True   # allows SQLAlchemy model → Pydantic

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