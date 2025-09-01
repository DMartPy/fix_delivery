from sqlalchemy import text

from dostavka.db.models import Base, PackageType
from dostavka.db.session import async_session, engine


async def init_package_types():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text("SELECT COUNT(*) FROM package_types"))
            count = result.scalar()

            if count == 0:
                types = [
                    PackageType(name="одежда"),
                    PackageType(name="электроника"),
                    PackageType(name="разное")
                ]
                session.add_all(types)
                await session.commit()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
