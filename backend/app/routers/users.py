from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import (
    get_user_service,
    get_current_user_id,
    get_email_code_service,
)
from backend.schemas.users import (
    UserRegister,
    UserOut,
    UserLogin,
    TokenOut,
    EmailCodeRequest,
    DevEmailCodeOut,
    PasswordResetConfirm,
    MessageOut,
    PasswordUpdate,
)
from backend.app.auth import create_access_token
from backend.app.settings import get_settings,Settings

router = APIRouter()


def user_to_dict(user):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

def build_email_code_response(message:str,dev_code:str, settings:Settings):
    if settings.app_env == "development" or settings.app_env == "test":
        return {
            "message": message,
            "dev_code": dev_code,
        }
    else:
        return {
            "message": message,
            "dev_code": None,
        }
# create a new user
# 暴露给前端的接口，前端发送请求，后端处理请求，返回响应 /users/register
@router.post("/register", response_model=UserOut)
def register_user(
    payload: UserRegister,
    user_service=Depends(get_user_service),
    email_code_service=Depends(get_email_code_service),
):
    try:
        verified = email_code_service.verify_code(
            payload.email,
            purpose="register",
            code=payload.verification_code,
        )

        if not verified:
            raise ValueError("Invalid or expired verification code")

        user_id = user_service.register_user(
            email=payload.email,
            username=payload.username,
            password=payload.password,
        )

        user = user_service.get_user(user_id)
        return user_to_dict(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# get the current user
@router.get("/me", response_model=UserOut)
def get_me(
    user_id: int = Depends(get_current_user_id),
    user_service=Depends(get_user_service),
):
    try:
        user = user_service.get_user(user_id)
        return user_to_dict(user)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/login", response_model=TokenOut)
def login_user(
    payload: UserLogin,
    user_service=Depends(get_user_service),
):
    try:
        user = user_service.login(payload.email, payload.password)
        return {
            "access_token": create_access_token(user.user_id),
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/register/send-code", response_model=DevEmailCodeOut)
def send_register_code(
    payload: EmailCodeRequest,
    user_service=Depends(get_user_service),
    email_code_service=Depends(get_email_code_service),
    settings:Settings = Depends(get_settings),
):
    try:
        if user_service.get_user_by_email(payload.email) is not None:
            raise ValueError("Email already exists")

        dev_code = email_code_service.generate_code(
            payload.email,
            purpose="register",
        )

        return build_email_code_response(
            message="Register verification code sent",
            dev_code=dev_code,
            settings=settings,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/password/reset", response_model=MessageOut)
def reset_password(
    payload: PasswordResetConfirm,
    user_service=Depends(get_user_service),
    email_code_service=Depends(get_email_code_service),
):
    try:
        verified = email_code_service.verify_code(
            payload.email,
            purpose="password_reset",
            code=payload.verification_code,
        )

        if not verified:
            raise ValueError("Invalid or expired verification code")

        user_service.reset_password_by_email(
            payload.email,
            payload.new_password,
        )

        return {"message": "Password reset successful"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/password/forgot/send-code", response_model=DevEmailCodeOut)
def send_password_reset_code(
    payload: EmailCodeRequest,
    user_service=Depends(get_user_service),
    email_code_service=Depends(get_email_code_service),
    settings:Settings = Depends(get_settings),
):
    try:
        if user_service.get_user_by_email(payload.email) is None:
            raise ValueError("User not found")

        dev_code = email_code_service.generate_code(
            payload.email,
            purpose="password_reset",
        )

        return build_email_code_response(
            message="Password reset code sent",
            dev_code=dev_code,
            settings=settings,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/me/password", response_model=MessageOut)
def update_my_password(
    payload: PasswordUpdate,
    user_id: int = Depends(get_current_user_id),
    user_service=Depends(get_user_service),
):
    try:
        user_service.change_password(
            user_id=user_id,
            old_password=payload.old_password,
            new_password=payload.new_password,
        )

        return {"message": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))