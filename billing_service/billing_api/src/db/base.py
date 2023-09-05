from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from config import settings


DATABASE_URL = f'postgresql+asyncpg://{settings.db.user}:{settings.db.password}' \
               f'@{settings.db.host}:{settings.db.port}/{settings.db.name}'
engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """ Dependency """
    async with async_session() as session:
        yield session
