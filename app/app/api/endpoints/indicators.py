from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import indicator as indicator_crud, unit as unit_crud
from app.schemas import indicator as schemas
from app.db.session import get_db
from app.data_processing.indicator import build_new_indicator

router = APIRouter()


@router.get("/", response_model=list[schemas.IndicatorShortDescriptionResponse])
async def read_indicators(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    indicators = await indicator_crud.get_indicators(db, skip=skip, limit=limit)
    response = []
    for indicator in indicators:
        # unit = await indicator.awaitable_attrs.unit
        response.append(
            schemas.IndicatorShortDescriptionResponse(
                id=indicator.id, name=indicator.name, unit_name=indicator.unit.unit_name
            )
        )
    return response


@router.post("/", response_model=schemas.IndicatorShortDescriptionResponse)
async def create_indicator(indicator: schemas.IndicatorCreateRequest, db: AsyncSession = Depends(get_db)):
    unit = await unit_crud.get_unit(db, indicator.unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Unit with id {indicator.unit_id} not found")
    indicator = await indicator_crud.create_indicator(db=db, indicator=indicator)
    unit = await indicator.awaitable_attrs.unit
    response = schemas.IndicatorShortDescriptionResponse(id=indicator.id, name=indicator.name, unit=unit.name)
    return response


@router.get("/{indicator_id}")
async def read_indicator_details(indicator_id: int, db: AsyncSession = Depends(get_db)):
    indicator = await indicator_crud.get_indicator(db, indicator_id=indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail=f"Indicator with id {indicator_id} not found")

    aggregated_values_availability = await indicator_crud.get_aggregated_indicator_values_availability(
        db, indicator_id=indicator_id
    )
    aggregated_availability_data = [schemas.IndicatorAvailability(**datum) for datum in aggregated_values_availability]
    detailed_values_availability = await indicator_crud.get_detailed_indicator_values_availability(
        db, indicator_id=indicator_id
    )
    detailed_availability_data = [schemas.IndicatorAvailability(**datum) for datum in detailed_values_availability]
    response = schemas.IndicatorFullDescriptionResponse(
        id=indicator.id,
        name=indicator.name,
        unit=indicator.unit.unit_name,
        aggregated_availability=aggregated_availability_data,
        detailed_availability=detailed_availability_data,
    )
    return response


@router.get("/{indicator_id}/{territory_id}", response_model=list[schemas.IndicatorAggregatedResponse])
async def read_aggregated_indicator_values(indicator_id: int, territory_id: int, db: AsyncSession = Depends(get_db)):
    indicators = await indicator_crud.get_aggregated_indicator_values(
        db, indicator_id=indicator_id, territory_id=territory_id
    )
    response = []
    for i in indicators:
        unit = await i.indicator.awaitable_attrs.unit
        response.append(
            schemas.IndicatorAggregatedResponse(
                id=i.id,
                indicator_id=i.indicator_id,
                name=i.indicator.name,
                unit=unit.unit_name,
                territory_id=i.territory_id,
                year=i.year,
                source=i.source,
                value=i.value,
            )
        )
    return response


@router.post("/{indicator_id}/{territory_id}", response_model=list[schemas.IndicatorAggregatedResponse])
async def load_aggregated_indicator_values(
    indicator_id: int,
    territory_id: int,
    indicator_values: list[schemas.LoadIndicatorAggregatedRequest],
    db: AsyncSession = Depends(get_db),
):
    # unit = await unit_crud.get_unit(db, indicator_value.unit_id)
    # if not unit:
    #     raise HTTPException(status_code=404, detail=f"Unit with id {indicator.unit_id} not found")
    # indicator = await indicator_crud.get_indicator(db, indicator_id=indicator_id)
    # if not indicator:
    #     raise HTTPException(status_code=404, detail=f"Indicator with id {indicator_id} not found")
    indicator_values = await indicator_crud.create_aggregated_indicator_values(
        db=db, indicator_id=indicator_id, territory_id=territory_id, indicator_values=indicator_values
    )

    indicators = await indicator_crud.get_aggregated_indicator_values(
        db, indicator_id=indicator_id, territory_id=territory_id
    )
    response = []
    for i in indicators:
        unit = await i.indicator.awaitable_attrs.unit
        response.append(
            schemas.IndicatorAggregatedResponse(
                id=i.id,
                indicator_id=i.indicator_id,
                name=i.indicator.name,
                unit=unit.unit_name,
                territory_id=i.territory_id,
                year=i.year,
                source=i.source,
                value=i.value,
            )
        )
    return response
