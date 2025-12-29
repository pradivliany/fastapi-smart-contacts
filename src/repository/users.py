from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.schemas.user_schemas import UserCreate


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    Retrieve a user by their email address.

    Args:
        email (str): Email of the user to search for.
        db (AsyncSession): Asynchronous database session.

    Returns:
        User | None: User object if found, otherwise None.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(body: UserCreate, db: AsyncSession) -> User:
    """
    Create a new user in the database.

    Args:
        body (UserCreate): Data for creating a new user, validated by Pydantic schema.
        db (AsyncSession): Asynchronous database session.

    Returns:
        User: Newly created User object after being saved in the database.
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_refresh_token(user: User, token: str | None, db: AsyncSession) -> None:
    """
    Update the refresh token for a given user.

    Args:
        user (User): User object whose refresh token will be updated.
        token (str | None): New refresh token or None to clear it.
        db (AsyncSession): Asynchronous database session.

    Returns:
        None
    """
    user.refresh_token = token
    await db.commit()
