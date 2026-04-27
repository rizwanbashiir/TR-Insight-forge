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
    name:     str
    email:    EmailStr
    password: str
    role:     UserRole = UserRole.analyst

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

# ── Response schemas (what server returns) ──
class UserResponse(BaseModel):
    id:         int
    name:       str
    email:      str
    role:       UserRole
    is_active:  bool
    created_at: datetime

    class Config:
        from_attributes = True   # allows SQLAlchemy model → Pydantic

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserResponse