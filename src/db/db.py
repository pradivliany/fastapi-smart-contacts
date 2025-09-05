import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

load_dotenv()


class Database:
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    PORT_DB = os.getenv("PORT_DB")
    HOST_DB = os.getenv("HOST_DB")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST_DB}:{PORT_DB}/{POSTGRES_DB}"

    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(self.DATABASE_URL)
        self.async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, autoflush=False
        )

    async def get_db(self):
        async with self.async_session_maker() as session:
            yield session
