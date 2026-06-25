from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    VerifyRequest, GoogleLoginRequest, RefreshTokenRequest,
    SetPasswordRequest, ResetPasswordRequest
)
from app.services.auth_services import (
    register_user, login_user, verify_email_code, register_or_login_google,
    create_access_token, create_refresh_token, refresh_access_token,
    set_new_password, send_forgot_password_link
)

router = APIRouter()

@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user  = register_user(db, data)
    return {"message": "Registration successful. Please check your email to verify your account."}

@router.post("/verify", response_model=TokenResponse)
def verify(data: VerifyRequest, db: Session = Depends(get_db)):
    user = verify_email_code(db, data.email, data.code)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": token, "refresh_token": refresh_token, "token_type": "bearer", "user": user}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, data)
    return {
        "access_token": result["token"],
        "refresh_token": result["refresh_token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/google", response_model=TokenResponse)
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    result = register_or_login_google(db, data.token)
    return {
        "access_token": result["token"],
        "refresh_token": result["refresh_token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    result = refresh_access_token(db, data.refresh_token)
    return {
        "access_token": result["token"],
        "refresh_token": result["refresh_token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/set-password")
def set_password(data: SetPasswordRequest, db: Session = Depends(get_db)):
    return set_new_password(db, data.token, data.new_password)

@router.post("/forgot-password")
def forgot_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return send_forgot_password_link(db, data.email)