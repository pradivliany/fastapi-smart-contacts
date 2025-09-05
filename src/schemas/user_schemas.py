from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    password: str


# валідація вхідних даних при реєстрації
class UserCreate(UserBase):
    pass


# валідація вихідних даних
class UserResponse(BaseModel):
    id: int
    email: EmailStr


# валідація вхідних даних при вході
class UserLogin(UserBase):
    pass


# модель валідації токенів
class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
