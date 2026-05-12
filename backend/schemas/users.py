from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    created_at: str
    updated_at: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"