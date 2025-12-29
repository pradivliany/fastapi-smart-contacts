from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    password: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: EmailStr


class UserLogin(UserBase):
    pass


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
