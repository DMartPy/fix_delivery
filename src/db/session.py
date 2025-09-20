from collections.abc import Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import REAL_DATABASE_URL

engine = create_async_engine(REAL_DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> Generator: # type: ignore
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
