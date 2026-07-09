from fastapi import APIRouter
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
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
async def register(data: RegisterRequest):
    await register_user(None, data)
    return {"message": "Registration successful. Please check your email to verify your account."}

@router.post("/verify")
async def verify(data: VerifyRequest):
    user = await verify_email_code(None, data.email, data.code)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login")
async def login(data: LoginRequest):
    result = await login_user(None, data)
    return {
        "access_token": result["token"],
        "refresh_token": result["refresh_token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/google")
async def google_login(data: GoogleLoginRequest):
    result = await register_or_login_google(None, data.token)
    return {
        "access_token": result["token"],
        "refresh_token": result["refresh_token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest):
    result = await refresh_access_token(None, data.refresh_token)
    return {
        "access_token": result["token"],
        "refresh_token": result["refresh_token"],
        "token_type":   "bearer",
        "user":         result["user"]
    }

@router.post("/set-password")
async def set_password(data: SetPasswordRequest):
    return await set_new_password(None, data.token, data.new_password)

@router.post("/forgot-password")
async def forgot_password(data: ResetPasswordRequest):
    return await send_forgot_password_link(None, data.email)