from sqlalchemy import text

from src.db.session import async_session, engine
from src.models.db import Base, PackageType


async def init_package_types():
    async with async_session() as session:
        async with session.begin():
            # Проверяем, есть ли уже типы посылок
            result = await session.execute(text("SELECT COUNT(*) FROM package_types"))
            count = result.scalar()
            
            if count == 0:
                # Создаем базовые типы посылок
                package_types = [
                    PackageType(name="Электроника"),
                    PackageType(name="Одежда"),
                    PackageType(name="Книги"),
                    PackageType(name="Продукты"),
                    PackageType(name="Другое")
                ]
                
                for package_type in package_types:
                    session.add(package_type)
                
                await session.commit()


async def create_tables():
    """Создать все таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
