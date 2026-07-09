from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from beanie import PydanticObjectId
import random
import requests

from app.config.settings import settings
from app.models.users import User, UserRole
from app.models.organizations import Organization
from app.models.subscriptions import Subscription
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.email_service import send_verification_email, send_password_reset_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Password helpers ──
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ── JWT helpers ──
def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ── Business logic ──
async def register_user(db, data: RegisterRequest) -> User:
    existing = await User.find_one(User.email == data.email)
    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            user = existing
    else:
        user = User(
            email=data.email,
            name="User",
            password=""
        )

    code = f"{random.randint(100000, 999999)}"
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    assigned_role = data.role
    if assigned_role == "admin":
        assigned_role = "analyst"

    full_name = data.name
    if not full_name and (data.first_name or data.last_name):
        full_name = f"{data.first_name or ''} {data.last_name or ''}".strip()
    if not full_name:
        full_name = "User"

    user.name = full_name
    user.first_name = data.first_name
    user.last_name = data.last_name
    user.org_name = data.org_name
    user.industry = data.industry
    user.team_size = data.team_size
    user.plan = data.plan
    user.password = hash_password(data.password)
    user.role = assigned_role
    user.is_active = False
    user.verification_code = code
    user.verification_expires = expires
    user.organization_id = None

    await user.save()
    send_verification_email(to_email=user.email, code=code)
    return user


async def verify_email_code(db, email: str, code: str) -> User:
    user = await User.find_one(User.email == email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified"
        )
    if user.verification_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    expires = user.verification_expires
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if expires and datetime.now(timezone.utc) > expires:
        new_code = f"{random.randint(100000, 999999)}"
        user.verification_code = new_code
        user.verification_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
        await user.save()
        send_verification_email(to_email=user.email, code=new_code)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. A new code has been generated and emailed to you."
        )

    user.is_active = True
    user.verification_code = None
    user.verification_expires = None

    if not user.organization_id:
        org_name = user.org_name or f"{user.name}'s Workspace"
        org = Organization(
            name=org_name,
            industry=user.industry,
            team_size=user.team_size
        )
        await org.insert()

        plan_tier = (user.plan or "free").lower()
        sub = Subscription(organization_id=org.id, plan_tier=plan_tier, status="active")
        await sub.insert()

        user.organization_id = org.id

    await user.save()
    return user


async def set_new_password(db, token: str, new_password: str):
    user = await User.find_one(User.reset_password_token == token)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")

    expires = user.reset_password_expires
    if expires and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if expires and datetime.now(timezone.utc) > expires:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")

    user.password = hash_password(new_password)
    user.password_changed = True
    user.reset_password_token = None
    user.reset_password_expires = None
    await user.save()
    return {"message": "Password updated successfully."}


async def send_forgot_password_link(db, email: str):
    user = await User.find_one(User.email == email)
    if not user:
        return {"message": "If an account exists with this email, a reset link has been sent."}

    from app.services.org_services import generate_reset_token
    token = generate_reset_token()
    user.reset_password_token = token
    user.reset_password_expires = datetime.now(timezone.utc) + timedelta(hours=6)
    await user.save()

    reset_link = f"http://localhost:5173/reset-password?token={token}"
    send_password_reset_email(to_email=email, reset_link=reset_link)

    return {"message": "If an account exists with this email, a reset link has been sent."}


async def login_user(db, data: LoginRequest) -> dict:
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in."
        )
    token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"token": token, "refresh_token": refresh_token, "user": user}


async def register_or_login_google(db, token: str) -> dict:
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        google_data = response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )

    if settings.GOOGLE_CLIENT_ID and google_data.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth audience mismatch"
        )

    email = google_data.get("email")
    name = google_data.get("name", "Google User")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token does not provide email"
        )

    user = await User.find_one(User.email == email)
    if not user:
        org = Organization(name=f"{name}'s Workspace")
        await org.insert()

        sub = Subscription(organization_id=org.id, plan_tier="free", status="active")
        await sub.insert()

        parts = name.split(" ", 1)
        first_name = google_data.get("given_name", parts[0])
        last_name = google_data.get("family_name", parts[1] if len(parts) > 1 else "")

        user = User(
            name=name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hash_password(f"google-oauth-{random.randint(100000, 999999)}"),
            role=UserRole.analyst,
            is_active=True,
            organization_id=org.id
        )
        await user.insert()
    elif not user.is_active:
        user.is_active = True
        await user.save()

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"token": access_token, "refresh_token": refresh_token, "user": user}


async def refresh_access_token(db, refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        try:
            oid = PydanticObjectId(user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id")

        user = await User.get(oid)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        new_access_token = create_access_token({"sub": str(user.id), "role": user.role})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        return {"token": new_access_token, "refresh_token": new_refresh_token, "user": user}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")