import calendar
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import Contact, User
from src.schemas.contact_schemas import (
    ContactCreate,
    ContactEmailUpdate,
    ContactResponse,
    ContactUpdate,
)


async def create_contact(body: ContactCreate, user: User, db: AsyncSession) -> Contact:
    """
    Create a new contact for the authenticated user.

    Args:
        body (ContactCreate): Contact data validated by Pydantic schema.
        user (User): Current authenticated user -> contact owner.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Contact: Created contact ORM object with related user loaded.

    Raises:
        HTTPException: If a contact with the same email already exists for the user.
    """
    result = await db.execute(
        select(Contact).where(
            and_(Contact.email == str(body.email), Contact.user_id == user.id)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already existing"
        )

    contact = Contact(**body.model_dump(), user_id=user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(Contact.id == contact.id)
    )

    return result.scalar_one()


async def read_contacts(
    skip: int, limit: int, user: User, db: AsyncSession
) -> list[Contact]:
    """
    Retrieve a paginated list of contacts for the authenticated user.

    Args:
        skip (int): Number of contacts to skip (offset).
        limit (int): Maximum number of contacts to return.
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        list[Contact]: List of user's contacts. Empty if no contacts.
    """
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(Contact.user_id == user.id)
        .offset(skip)
        .limit(limit)
    )
    contacts = list(result.scalars().all())
    return contacts


async def read_contact(contact_id: int, user: User, db: AsyncSession) -> Contact | None:
    """
    Retrieve a single contact by ID for the authenticated user.

    Args:
        contact_id (int): ID of the contact to retrieve.
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Contact | None: Contact if found and owned by the user, otherwise None.
    """
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    return result.scalar_one_or_none()


async def update_contact(
    body: ContactUpdate, contact_id: int, user: User, db: AsyncSession
) -> Contact | None:
    """
    Update an existing contact owned by the authenticated user.

    Args:
        body (ContactUpdate): Updated contact data validated by Pydantic schema.
        contact_id (int): ID of the contact to update.
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Contact | None: Updated contact if found and owned by the user, otherwise None.

    Raises:
        HTTPException: 409 Conflict if the provided email is already in use.
    """
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    contact = result.scalar_one_or_none()

    if not contact:
        return None

    result2 = await db.execute(
        select(Contact).where(
            and_(
                Contact.email == str(body.email),
                Contact.id != contact_id,
                Contact.user_id == user.id,
            )
        )
    )
    existing_email = result2.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already existing email"
        )

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = str(body.email)
    contact.phone_number = body.phone_number
    contact.date_of_birth = body.date_of_birth
    contact.additional_info = body.additional_info

    await db.commit()
    await db.refresh(contact)

    return contact


async def update_email_contact(
    body: ContactEmailUpdate, contact_id: int, user: User, db: AsyncSession
) -> Contact | None:
    """
    Update the email address of an existing contact owned by the authenticated user.

    Args:
        body (ContactEmailUpdate): New email data validated by Pydantic schema.
        contact_id (int): ID of the contact to update.
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        Contact | None: Updated contact if found and owned by the user, otherwise None.

    Raises:
        HTTPException: 409 Conflict if the provided email is already in use.
    """
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    contact = result.scalar_one_or_none()

    if not contact:
        return None

    result2 = await db.execute(
        select(Contact).where(
            and_(
                Contact.email == str(body.email),
                Contact.id != contact_id,
                Contact.user_id == user.id,
            )
        )
    )
    existing_email = result2.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Already existing email"
        )

    contact.email = str(body.email)

    await db.commit()
    await db.refresh(contact)

    return contact


async def delete_contact(
    contact_id: int, user: User, db: AsyncSession
) -> ContactResponse | None:
    """
    Delete an existing contact owned by the authenticated user.

    Args:
        contact_id (int): ID of the contact to delete.
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        ContactResponse | None: Deleted contact data if found and deleted, otherwise None.
    """
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(and_(Contact.id == contact_id, Contact.user_id == user.id))
    )
    contact = result.scalar_one_or_none()

    if not contact:
        return None

    contact_response = ContactResponse.model_validate(contact)

    await db.delete(contact)
    await db.commit()

    return contact_response


async def search_contact(
    first_name: str, last_name: str, email: str, user: User, db: AsyncSession
) -> list[Contact]:
    """
    Search for contacts owned by the authenticated user using optional filters.

    Args:
        first_name (str): First name to filter by (optional).
        last_name (str): Last name to filter by (optional).
        email (str): Email to filter by (optional).
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        list[Contact]: List of contacts matching the filters. Empty list if none found.
    """
    stmt = (
        select(Contact)
        .options(selectinload(Contact.user))
        .where(Contact.user_id == user.id)
    )

    if first_name:
        stmt = stmt.where(Contact.first_name == first_name)
    if last_name:
        stmt = stmt.where(Contact.last_name == last_name)
    if email:
        stmt = stmt.where(Contact.email == email)

    result = await db.execute(stmt)
    return list(result.scalars().all())


def helpful_func(my_date: date, next_date: date) -> bool:
    """
    Check if 'next_date' falls within 7 days after `my_date`, accounting for year boundaries.

    Args:
        my_date (date): Reference date.
        next_date (date): Date to check against the 7-day window.

    Returns:
        bool: True if `next_date` is within 7 days after `my_date`, False otherwise.
    """
    month1_date1_tuple = (my_date.month, my_date.day)
    base_year = 2020 if calendar.isleap(my_date.year) else 2021

    # If the date is before December 25th (<25)
    if month1_date1_tuple < (12, 25):
        my_date_leap = date(year=base_year, month=my_date.month, day=my_date.day)
        next_date_leap = date(year=base_year, month=next_date.month, day=next_date.day)
        difference = next_date_leap.toordinal() - my_date_leap.toordinal()
        return 1 <= difference <= 7

    # If the date is on or after December 25th
    else:
        my_date_leap = date(year=base_year, month=my_date.month, day=my_date.day)
        next_7_days = [my_date_leap + timedelta(days=i) for i in range(1, 8)]
        next_date_leap = (
            date(year=base_year, month=next_date.month, day=next_date.day)
            if next_date.month == 12
            else date(year=base_year + 1, month=next_date.month, day=next_date.day)
        )
        return next_date_leap in next_7_days


async def find_next_birthdays_in_7_days(user: User, db: AsyncSession) -> list[Contact]:
    """
    Find contacts of the authenticated user whose birthdays occur within the next 7 days.

    Args:
        user (User): Current authenticated user.
        db (AsyncSession): Asynchronous database session.

    Returns:
        list[Contact]: List of contacts with birthdays in the next 7 days. Empty list if none found.
    """
    today_date = date.today()
    result = await db.execute(
        select(Contact)
        .options(selectinload(Contact.user))
        .where(Contact.user_id == user.id)
    )
    all_contacts = list(result.scalars().all())

    return [
        contact
        for contact in all_contacts
        if helpful_func(today_date, contact.date_of_birth)
    ]
