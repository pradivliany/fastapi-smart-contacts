import calendar
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Contact
from src.schemas.contact_schemas import ContactCreate, ContactEmailUpdate, ContactUpdate


async def create_contact(body: ContactCreate, db: AsyncSession) -> Contact:
    result = await db.execute(select(Contact).where(Contact.email == str(body.email)))
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already existing"
        )

    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=str(body.email),
        phone_number=body.phone_number,
        date_of_birth=body.date_of_birth,
        additional_info=body.additional_info,
    )

    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def read_contacts(skip: int, limit: int, db: AsyncSession) -> list[Contact]:
    result = await db.execute(select(Contact).offset(skip).limit(limit))
    contacts = list(result.scalars().all())
    return contacts


async def read_contact(contact_id: int, db: AsyncSession) -> Contact | None:
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    return result.scalar_one_or_none()


async def update_contact(
    body: ContactUpdate, contact_id: int, db: AsyncSession
) -> Contact | None:
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()

    if not contact:
        return None

    result2 = await db.execute(
        select(Contact).where(
            and_(Contact.email == str(body.email), Contact.id != contact_id)
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
    body: ContactEmailUpdate, contact_id: int, db: AsyncSession
) -> Contact | None:
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()

    if not contact:
        return None

    result2 = await db.execute(
        select(Contact).where(
            and_(Contact.email == str(body.email), Contact.id != contact_id)
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


async def delete_contact(contact_id: int, db: AsyncSession) -> Contact | None:
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()

    if contact:
        await db.delete(contact)
        await db.commit()

    return contact


async def search_contact(
    first_name: str, last_name: str, email: str, db: AsyncSession
) -> list[Contact]:
    stmt = select(Contact)

    if first_name:
        stmt = stmt.where(Contact.first_name == first_name)
    if last_name:
        stmt = stmt.where(Contact.last_name == last_name)
    if email:
        stmt = stmt.where(Contact.email == email)

    result = await db.execute(stmt)
    return list(result.scalars().all())


def helpful_func(my_date, next_date):
    month1_date1_tuple = (my_date.month, my_date.day)
    base_year = 2020 if calendar.isleap(my_date.year) else 2021

    # Якщо дата до 24-го грудня (включно)
    if month1_date1_tuple < (12, 25):
        my_date_leap = date(year=base_year, month=my_date.month, day=my_date.day)
        next_date_leap = date(year=base_year, month=next_date.month, day=next_date.day)
        difference = next_date_leap.toordinal() - my_date_leap.toordinal()
        return 1 <= difference <= 7

    # якщо після 25-го грудня (включно)
    else:
        my_date_leap = date(year=base_year, month=my_date.month, day=my_date.day)
        next_7_days = [my_date_leap + timedelta(days=i) for i in range(1, 8)]
        next_date_leap = (
            date(year=base_year, month=next_date.month, day=next_date.day)
            if next_date.month == 12
            else date(year=base_year + 1, month=next_date.month, day=next_date.day)
        )
        return next_date_leap in next_7_days


async def find_next_birthdays_in_7_days(db: AsyncSession) -> list[Contact]:
    today_date = date.today()
    result = await db.execute(select(Contact))
    all_contacts = list(result.scalars().all())

    return [
        contact
        for contact in all_contacts
        if helpful_func(today_date, contact.date_of_birth)
    ]
