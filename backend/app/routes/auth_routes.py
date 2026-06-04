from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    VerifyRequest, GoogleLoginRequest
)
from app.services.auth_services import (
    register_user, login_user, verify_email_code, register_or_login_google
)

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user  = register_user(db, data)
    token = __import__('app.services.auth_services',
                        fromlist=['create_access_token']).create_access_token(
        {"sub": str(user.id), "role": user.role}
    )
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/verify", response_model=UserResponse)
def verify(data: VerifyRequest, db: Session = Depends(get_db)):
    user = verify_email_code(db, data.email, data.code)
    return user

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, data)
    return {
        "access_token": result["token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/google", response_model=TokenResponse)
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    result = register_or_login_google(db, data.token)
    return {
        "access_token": result["token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }