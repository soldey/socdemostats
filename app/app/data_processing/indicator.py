from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import unit as unit_crud, indicator as indicator_crud
from app.schemas import indicator as indicator_schemas, unit as unit_schemas
from fastapi import HTTPException


async def build_new_indicator(db: AsyncSession, indicator: indicator_schemas.IndicatorCreateRequest):
    unit = await unit_crud.get_unit(db, indicator.unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return await indicator_crud.create_indicator(db, indicator, unit)
