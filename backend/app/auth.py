from datetime import datetime, timedelta,timezone
import jwt
from fastapi import HTTPException
from backend.app.settings import get_settings,Settings

# function to create access token, used to authenticate user
def create_access_token(user_id: int):
    settings=get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

# function to decode access token, used to get user id from token
def decode_access_token(token: str) -> int:
    settings=get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if user_id <= 0:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id