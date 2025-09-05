from datetime import date

from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    first_name: str = Field(max_length=50, min_length=2)
    last_name: str = Field(max_length=50, min_length=2)
    email: EmailStr = Field(max_length=100)
    phone_number: str = Field(pattern=r"^(\+38)?\d{10}$")
    date_of_birth: date
    additional_info: str | None = Field(default=None, max_length=100)


class ContactResponse(ContactCreate):
    id: int


class ContactUpdate(ContactCreate):
    pass


class ContactEmailUpdate(BaseModel):
    email: EmailStr = Field(max_length=100)
