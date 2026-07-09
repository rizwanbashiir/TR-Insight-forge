from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime, timezone
import enum

class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin   = "admin"
    analyst = "analyst"
    viewer  = "viewer"

class User(Document):
    organization_id: Optional[PydanticObjectId] = None
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    org_name: Optional[str] = None
    industry: Optional[str] = None
    team_size: Optional[str] = None
    plan: Optional[str] = None
    email: str
    password: str
    role: UserRole = UserRole.analyst
    is_active: bool = False
    verification_code: Optional[str] = None
    verification_expires: Optional[datetime] = None
    password_changed: bool = False
    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"