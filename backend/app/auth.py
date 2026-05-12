from datetime import datetime, timedelta,timezone
import jwt
from fastapi import HTTPException
import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-minimum-32-bytes-long") # if not set, use a default value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24

# function to create access token, used to authenticate user
def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# function to decode access token, used to get user id from token
def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if user_id <= 0:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id