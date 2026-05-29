from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    verification_code: str = Field(min_length=6, max_length=6)


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


class EmailCodeRequest(BaseModel):
    email: EmailStr


class DevEmailCodeOut(BaseModel):
    message: str
    dev_code: str | None = None


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    verification_code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=6)


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


class MessageOut(BaseModel):
    message: str

