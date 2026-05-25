from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import get_user_service, get_current_user_id
from backend.schemas.users import UserRegister, UserOut, UserLogin, TokenOut, EmailCodeRequest, DevEmailCodeOut, PasswordResetConfirm, MessageOut, PasswordUpdate
from backend.app.auth import create_access_token

router = APIRouter()


def user_to_dict(user):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "username": user.username,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

# create a new user
# 暴露给前端的接口，前端发送请求，后端处理请求，返回响应 /users/register
@router.post("/register", response_model=UserOut)
def register_user(
    payload: UserRegister,
    user_service=Depends(get_user_service),
):
    try:
        user_id = user_service.register_user(
            email=payload.email,
            username=payload.username,
            password=payload.password,
            verification_code=payload.verification_code,
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

@router.post("/email/code", response_model=DevEmailCodeOut)
def send_email_code(
    payload: EmailCodeRequest,
    user_service=Depends(get_user_service),
):
    try:
        user_service.send_email_code(payload.email)
        return {"message": "Email code sent", "dev_code": dev_code}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/password/reset", response_model=MessageOut)
def reset_password(
    payload: PasswordResetConfirm,
    user_service=Depends(get_user_service),
):
    try:
        user_service.reset_password(payload.email, payload.verification_code, payload.new_password)
        return {"message": "Password reset successful"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forget/send_code", response_model=MessageOut)
def send_forget_code(
    payload: EmailCodeRequest,
    user_service=Depends(get_user_service),
):
    try:
        user_service.send_forget_code(payload.email)
        return {"message": "Forget code sent"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))