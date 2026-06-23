from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import random
import requests

from app.config.settings import settings
from app.models.users import User
from app.schemas.auth import RegisterRequest, LoginRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Password helpers ──
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ── JWT helpers ──
def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY,
                          algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# ── Business logic ──
def register_user(db: Session, data: RegisterRequest) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate 6-digit verification code
    code = f"{random.randint(100000, 999999)}"
    expires = datetime.utcnow() + timedelta(minutes=10)

    # Auto-create organization and subscription for new user
    from app.models.organizations import Organization
    from app.models.subscriptions import Subscription

    org = Organization(name=f"{data.name}'s Workspace")
    db.add(org)
    db.flush()  # gets the ID

    sub = Subscription(organization_id=org.id, plan_tier="free", status="active")
    db.add(sub)

    # Forbid admin role on public signup
    assigned_role = data.role
    if assigned_role == "admin":
        assigned_role = "analyst"

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=assigned_role,
        is_active=False,
        verification_code=code,
        verification_expires=expires,
        organization_id=org.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Print verification code to console for development/test purposes
    print(f"\n==========================================")
    print(f"VERIFICATION CODE FOR {user.email}: {code}")
    print(f"==========================================\n")

    return user

def verify_email_code(db: Session, email: str, code: str) -> User:
    user = db.query(User).filter(User.email == email).first()
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
    if expires and expires.tzinfo is not None:
        expires = expires.replace(tzinfo=None)

    if expires and datetime.utcnow() > expires:
        # Code expired — generate a new one
        new_code = f"{random.randint(100000, 999999)}"
        user.verification_code = new_code
        user.verification_expires = datetime.utcnow() + timedelta(minutes=10)
        db.commit()
        print(f"\n==========================================")
        print(f"NEW VERIFICATION CODE FOR {user.email}: {new_code}")
        print(f"==========================================\n")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired. A new code has been generated and printed to the console."
        )

    user.is_active = True
    user.verification_code = None
    user.verification_expires = None
    db.commit()
    db.refresh(user)
    return user

def set_new_password(db: Session, token: str, new_password: str):
    user = db.query(User).filter(User.reset_password_token == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
        
    expires = user.reset_password_expires
    if expires and expires.tzinfo is not None:
        expires = expires.replace(tzinfo=None)
        
    if expires and datetime.utcnow() > expires:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")
        
    user.password = hash_password(new_password)
    user.password_changed = True
    user.reset_password_token = None
    user.reset_password_expires = None
    db.commit()
    return {"message": "Password updated successfully."}

def send_forgot_password_link(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't leak if user exists
        return {"message": "If an account exists with this email, a reset link has been sent."}
        
    from app.services.org_services import generate_reset_token
    token = generate_reset_token()
    user.reset_password_token = token
    user.reset_password_expires = datetime.utcnow() + timedelta(hours=6)
    db.commit()
    
    print("\n" + "="*50)
    print(f"PASSWORD RESET EMAIL SENT TO: {email}")
    print(f"Please use this reset link:")
    print(f"http://localhost:5173/reset-password?token={token}")
    print(f"(Link valid for 6 hours)")
    print("="*50 + "\n")
    
    return {"message": "If an account exists with this email, a reset link has been sent."}

def login_user(db: Session, data: LoginRequest) -> dict:
    user = db.query(User).filter(User.email == data.email).first()
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

def register_or_login_google(db: Session, token: str) -> dict:
    # 1. Verify token with Google API
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

    # 2. Check client ID if configured
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

    # 3. Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        from app.models.organizations import Organization
        from app.models.subscriptions import Subscription

        org = Organization(name=f"{name}'s Workspace")
        db.add(org)
        db.flush()

        sub = Subscription(organization_id=org.id, plan_tier="free", status="active")
        db.add(sub)

        user = User(
            name=name,
            email=email,
            password=hash_password(f"google-oauth-{random.randint(100000, 999999)}"),
            role="analyst",
            is_active=True,
            organization_id=org.id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.is_active:
        user.is_active = True
        db.commit()
        db.refresh(user)

    # 4. Generate JWT
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"token": access_token, "refresh_token": refresh_token, "user": user}

def refresh_access_token(db: Session, refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
            
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
            
        new_access_token = create_access_token({"sub": str(user.id), "role": user.role})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        return {"token": new_access_token, "refresh_token": new_refresh_token, "user": user}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")