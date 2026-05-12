from fastapi import APIRouter, Depends, HTTPException

from backend.app.deps import get_user_service, get_current_user_id
from backend.schemas.users import UserRegister, UserOut, UserLogin, TokenOut
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