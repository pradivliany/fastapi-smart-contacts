from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.crud import contacts as crud_contacts
from src.db.db import get_db
from src.schemas.schemas import (
    ContactCreate,
    ContactEmailUpdate,
    ContactResponse,
    ContactUpdate,
)

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    return await crud_contacts.create_contact(body, db)


@router.get("/", response_model=list[ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await crud_contacts.read_contacts(skip, limit, db)
    return contacts


@router.get("/search/birthdays", response_model=list[ContactResponse])
async def find_next_birthdays_in_7_days(db: Session = Depends(get_db)):
    contacts = await crud_contacts.find_next_birthdays_in_7_days(db)
    return contacts


@router.get("/search", response_model=list[ContactResponse])
async def search_contact(
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_db),
):
    contacts = await crud_contacts.search_contact(first_name, last_name, email, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await crud_contacts.read_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate, contact_id: int, db: Session = Depends(get_db)
):
    contact = await crud_contacts.update_contact(body, contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_email_contact(
    body: ContactEmailUpdate, contact_id: int, db: Session = Depends(get_db)
):
    contact = await crud_contacts.update_email_contact(body, contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await crud_contacts.delete_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
