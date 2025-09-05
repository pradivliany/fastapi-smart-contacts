from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.db import Database
from src.db.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact_schemas import (ContactCreate, ContactEmailUpdate,
                                         ContactResponse, ContactUpdate)
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])
database = Database()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    return await repository_contacts.create_contact(body, current_user, db)


@router.get("/", response_model=list[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contacts = await repository_contacts.read_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/search/birthdays", response_model=list[ContactResponse])
async def find_next_birthdays_in_7_days(
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contacts = await repository_contacts.find_next_birthdays_in_7_days(current_user, db)
    return contacts


@router.get("/search", response_model=list[ContactResponse])
async def search_contact(
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contacts = await repository_contacts.search_contact(
        first_name, last_name, email, current_user, db
    )
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contact = await repository_contacts.read_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contact = await repository_contacts.update_contact(
        body, contact_id, current_user, db
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_email_contact(
    body: ContactEmailUpdate,
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contact = await repository_contacts.update_email_contact(
        body, contact_id, current_user, db
    )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(database.get_db),
):
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
