from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.unit import Unit
from app.schemas.unit import UnitCreateRequest


async def get_unit(db: AsyncSession, unit_id: int) -> Unit:
    result = await db.execute(select(Unit).filter(Unit.id == unit_id))
    return result.scalars().first()


async def create_unit(db: AsyncSession, unit: UnitCreateRequest) -> Unit:
    existent_units = await db.execute(select(Unit).filter(Unit.name == unit.name))
    existent_unit = existent_units.scalars().first()
    if existent_unit:
        return existent_unit
    db_unit = Unit(name=unit.name)
    db.add(db_unit)
    await db.commit()
    await db.refresh(db_unit)
    return db_unit


async def get_units(db: AsyncSession, skip: int = 0, limit: int = 10) -> Unit:
    result = await db.execute(select(Unit).offset(skip).limit(limit))
    return result.scalars().all()
