from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.schemas.user_schemas import UserCreate


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    [ПРИЙМАЄ] -> email: str це email користувача, що шукаємо
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Об'єкт моделі ОРМ User або None, якщо користувача з таким email не знайдено
    [ЛОГІКА] -> Виконується асинхронний запит до БД з фільтром по email, повертається перший знайдений об'єкт
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(body: UserCreate, db: AsyncSession) -> User:
    """
    [ПРИЙМАЄ] -> body: UserCreate це дані для створення нового користувача (валідуються Pydantic-схемою)
                 db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> Об'єкт моделі ОРМ User після збереження у БД
    [ЛОГІКА] -> Створюємо новий об'єкт User з даних body, додаємо його в сесію, комітимо і оновлюємо стан об'єкта
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_refresh_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    [ПРИЙМАЄ] -> user: User це об'єкт користувача, у якого оновлюємо токен
                token: str | None це новий refresh_token або None
                db: AsyncSession це об'єкт асинхронного підключення до БД
    [ПОВЕРТАЄ] -> None
    [ЛОГІКА] -> Присвоюємо переданий token у поле refresh_token користувача та комітимо зміни в БД
    """
    user.refresh_token = token
    await db.commit()
