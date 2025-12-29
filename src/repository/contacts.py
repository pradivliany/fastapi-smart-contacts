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
    [ПРИЙМАЄ] -> body: ContactCreate це є тілом запиту (валідується відповідною Pydantic-схемою)
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Об'єкт моделі ОРМ Contact
    [ЛОГІКА] -> Виконується асинхронний запит до БД в якому додається створений новий об'єкт Контакту. + повернення
    [ПРИМІТКА] -> Можливий виняток HTTPException якщо емеіл вже існує в БД
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
    [ПРИЙМАЄ] -> skip: int це щоб показати скільки контактів пропустити від початку,
                 limit: int це щоб покакати скільки контактів відобразити
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> list[Contact] список контактів або пустий список
    [ЛОГІКА] -> Виконується асинхронний запит до БД в якому читаються контакти відповідного user. + повернення
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
    [ПРИЙМАЄ] -> contact_id: int це ідентифікатор конкретного контакту,
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Contact | None це повернення або контакту або None(якщо не існує)
    [ЛОГІКА] -> Виконується асинхронний запит до БД в якому читається контакт відповідного user. + повернення
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
    [ПРИЙМАЄ] -> body: ContactUpdate це є тілом запиту (валідується відповідною Pydantic-схемою)
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Об'єкт моделі ОРМ Contact або None (якщо контакту не існує)
    [ЛОГІКА] -> Виконується асинхронний запит до БД в якому спершу первіряється наявність контакту, потім унікальність
                меілу, а потім змінюється об'єкт Контакту. + повернення
    [ПРИМІТКА] -> Можливий виняток HTTPException якщо емеіл (на який ми хочемо змінити) вже існує в БД
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
    [ПРИЙМАЄ] -> body: ContactEmailUpdate це є тілом запиту (валідується відповідною Pydantic-схемою)
                 contact_id: int це ідентифікатор конкретного контакту
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Об'єкт моделі ОРМ Contact або None (якщо контакту не існує)
    [ЛОГІКА] -> Виконується асинхронний запит до БД в якому спершу перевіряється наявність контакту,
                потім перевіряється унікальність нового email у рамках користувача,
                а потім змінюється поле email. + повернення
    [ПРИМІТКА] -> Можливий виняток HTTPException якщо email (на який ми хочемо змінити) вже існує в БД
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
    [ПРИЙМАЄ] -> contact_id: int це ідентифікатор конкретного контакту
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Об'єкт моделі ОРМ Contact або None (якщо контакту не існує)
    [ЛОГІКА] -> Виконується асинхронний запит до БД в якому спершу перевіряється наявність контакту,
                а потім, якщо він існує, видаляється об'єкт Контакту. + повернення
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
    [ПРИЙМАЄ] -> first_name: str ім'я для пошуку (може бути порожнім)
                 last_name: str прізвище для пошуку (може бути порожнім)
                 email: str email для пошуку (може бути порожнім)
                 user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> список Contact, що відповідають умовам пошуку, або пустий список
    [ЛОГІКА] -> Виконується асинхронний запит до БД з фільтрацією по переданих аргументах. + повернення
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


async def find_next_birthdays_in_7_days(user: User, db: AsyncSession) -> list[Contact]:
    """
    [ПРИЙМАЄ] -> user: User це екземпляр класу User, тобто той кому належать контакти
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> список Contact, що мають день народження протягом наступних 7 днів, або пустий список
    [ЛОГІКА] -> Виконується асинхронний запит до БД для отримання всіх контактів конкретного user,
                потім за допомогою допоміжної функції helpful_func фільтруються контакти за датою народження.+повернення
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
