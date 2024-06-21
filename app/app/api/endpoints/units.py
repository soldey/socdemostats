from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import unit as crud
from app.schemas.unit import UnitCreateRequest, UnitResponse
from app.db.session import get_db

router = APIRouter()

@router.get("/{unit_id}", response_model=UnitResponse)
async def read_unit(unit_id: int, db: AsyncSession = Depends(get_db)):
    unit = await crud.get_unit(db, unit_id=unit_id)
    return unit

@router.get("/", response_model=list[UnitResponse])
async def read_units(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    units = await crud.get_units(db, skip=skip, limit=limit)
    return units

@router.post("/", response_model=UnitResponse)
async def create_unit(unit: UnitCreateRequest, db: AsyncSession = Depends(get_db)):
    return await crud.create_unit(db=db, unit=unit)