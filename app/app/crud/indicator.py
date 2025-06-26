from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, distinct
from app.models import indicator as indicator_models, unit as unit_models
from app.schemas import indicator as schemas
from sqlalchemy.orm import selectinload, joinedload


async def get_indicators(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[indicator_models.Indicator]:
    result = await db.execute(
        select(indicator_models.Indicator)
        .options(joinedload(indicator_models.Indicator.unit))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_indicator(db: AsyncSession, indicator_id: int) -> indicator_models.Indicator:
    result = await db.execute(
        select(indicator_models.Indicator)
        .options(joinedload(indicator_models.Indicator.unit))
        .filter(indicator_models.Indicator.id == indicator_id)
    )
    return result.scalars().first()


async def create_indicator(db: AsyncSession, indicator: schemas.IndicatorCreateRequest) -> indicator_models.Indicator:
    existent_indicators = await db.execute(
        select(indicator_models.Indicator).where(
            indicator_models.Indicator.name == indicator.name, indicator_models.Indicator.unit_id == indicator.unit_id
        )
    )
    existent_indicator = existent_indicators.scalars().first()
    if existent_indicator:
        return existent_indicator
    db_indicator = indicator_models.Indicator(name=indicator.name, unit_id=indicator.unit_id)
    db.add(db_indicator)
    await db.commit()
    await db.refresh(db_indicator)
    return db_indicator


async def get_aggregated_indicator_values_availability(db: AsyncSession, indicator_id: int):
    result = await db.execute(
        select(indicator_models.AggregatedIndicatorValue).filter(
            indicator_models.AggregatedIndicatorValue.indicator_id == indicator_id
        )
    )

    return [
        {"year": row.year, "territory_id": row.territory_id, "source": row.source, "oktmo": row.oktmo} for row in result.scalars().all()
    ]


async def get_detailed_indicator_values_availability(db: AsyncSession, indicator_id: int):
    result = await db.execute(
        select(indicator_models.DetailedIndicatorValue).filter(
            indicator_models.DetailedIndicatorValue.indicator_id == indicator_id
        )
    )

    return [
        {"year": row.year, "territory_id": row.territory_id, "source": row.source, "oktmo": row.oktmo} for row in result.scalars().all()
    ]


async def create_aggregated_indicator_values(
    db: AsyncSession,
    indicator_id: int,
    territory_id: Optional[int],
    oktmo: Optional[int],
    indicator_values: list[schemas.LoadIndicatorAggregatedRequest],
):
    if not territory_id and not oktmo:
        raise HTTPException(400, "TERRITORY_ID_OR_OKTMO_NOT_PROVIDED")
    # indicator = await get_indicator(db, indicator_id)
    for indicator_value in indicator_values:
        query = select(indicator_models.AggregatedIndicatorValue).where(
            indicator_models.AggregatedIndicatorValue.indicator_id == indicator_id,
            indicator_models.AggregatedIndicatorValue.year == indicator_value.year,
        )
        if oktmo:
            query = query.where(indicator_models.AggregatedIndicatorValue.oktmo == oktmo)
        else:
            query = query.where(indicator_models.AggregatedIndicatorValue.territory_id == territory_id)
        result = await db.execute(query)
        if result.scalars().all():
            query = (
                update(indicator_models.AggregatedIndicatorValue)
                .where(
                    indicator_models.AggregatedIndicatorValue.indicator_id == indicator_id,
                    indicator_models.AggregatedIndicatorValue.year == indicator_value.year,
                )
            )
            if oktmo:
                query = query.where(indicator_models.AggregatedIndicatorValue.oktmo == oktmo)
            else:
                query = query.where(indicator_models.AggregatedIndicatorValue.territory_id == territory_id)
            query = query.values(value=indicator_value.value, source=indicator_value.source)
            await db.execute(query)
        else:
            db_indicator_aggregated_value = indicator_models.AggregatedIndicatorValue(
                indicator_id=indicator_id,
                territory_id=territory_id,
                oktmo=oktmo,
                year=indicator_value.year,
                value=indicator_value.value,
                source=indicator_value.source,
            )
            db.add(db_indicator_aggregated_value)
    await db.commit()


async def get_aggregated_indicator_values(
        db: AsyncSession,
        indicator_id: int,
        territory_id: Optional[int],
        oktmo: Optional[int],
        year: int = None
):
    if not territory_id and not oktmo:
        raise HTTPException(400, "TERRITORY_ID_OR_OKTMO_NOT_PROVIDED")
    query = (
        select(indicator_models.AggregatedIndicatorValue)
        .where(
            indicator_models.AggregatedIndicatorValue.indicator_id == indicator_id,
            indicator_models.AggregatedIndicatorValue.territory_id == territory_id,
        )
        .options(joinedload(indicator_models.AggregatedIndicatorValue.indicator))
    )
    if year:
        query = query.where(indicator_models.AggregatedIndicatorValue.year == year)
    if oktmo:
        query = query.where(indicator_models.AggregatedIndicatorValue.oktmo == oktmo)
    else:
        query = query.where(indicator_models.AggregatedIndicatorValue.territory_id == territory_id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_detailed_indicator_values(
    db: AsyncSession, indicator_id: int, territory_id: Optional[int], oktmo: Optional[int], year: int | None = None
) -> list[schemas.IndicatorDetailedResponse] | None:
    if not territory_id and not oktmo:
        raise HTTPException(400, "TERRITORY_ID_OR_OKTMO_NOT_PROVIDED")
    query = (
        select(indicator_models.DetailedIndicatorValue)
        .options(joinedload(indicator_models.DetailedIndicatorValue.indicator))
        .order_by(indicator_models.DetailedIndicatorValue.age_start)
    )

    if oktmo:
        query = query.filter(
            indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
            indicator_models.DetailedIndicatorValue.oktmo == oktmo,
        )
    else:
        query = query.filter(
            indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
            indicator_models.DetailedIndicatorValue.territory_id == territory_id,
        )
    if year is not None:
        query = query.filter(indicator_models.DetailedIndicatorValue.year == year)

    result = await db.execute(query)
    values = result.scalars().all()

    if not values:
        return None

    # Group by year if year is None
    values_by_year: dict[schemas.IndicatorUniqueDetailedPair, list[schemas.DetailedIndicatorValue]] = {}
    for value in values:
        pair = schemas.IndicatorUniqueDetailedPair(year=value.year, source=value.source)
        if pair not in values_by_year:
            values_by_year[pair] = []
        values_by_year[pair].append(value)

    responses = []
    for pair, values in values_by_year.items():
        first_value = values[0]
        unit = await first_value.indicator.awaitable_attrs.unit
        response = schemas.IndicatorDetailedResponse(
            indicator_id=indicator_id,
            territory_id=first_value.territory_id,
            oktmo=first_value.oktmo,
            unit=unit.unit_name,
            year=pair.year,
            source=pair.source,
            data=[
                schemas.IndicatorDetailedData(
                    age_start=value.age_start, age_end=value.age_end, male=value.male, female=value.female
                )
                for value in values
            ],
        )
        responses.append(response)

    return responses


async def load_detailed_indicator_values(
    db: AsyncSession,
    indicator_id: int,
    territory_id: Optional[int],
    oktmo: Optional[int],
    request: schemas.LoadIndicatorDetailedRequest
) -> list[indicator_models.DetailedIndicatorValue]:
    if not territory_id and not oktmo:
        raise HTTPException(400, "TERRITORY_ID_OR_OKTMO_NOT_PROVIDED")
    for data in request.data:
        query = (
            select(indicator_models.DetailedIndicatorValue)
            .options(joinedload(indicator_models.DetailedIndicatorValue.indicator))
            .filter(
                indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
                indicator_models.DetailedIndicatorValue.territory_id == territory_id,
                indicator_models.DetailedIndicatorValue.age_start == data.age_start,
                indicator_models.DetailedIndicatorValue.age_end == data.age_end,
                indicator_models.DetailedIndicatorValue.year == request.year,
            )
        )

        if oktmo:
            query = query.filter(
                indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
                indicator_models.DetailedIndicatorValue.oktmo == oktmo,
                indicator_models.DetailedIndicatorValue.age_start == data.age_start,
                indicator_models.DetailedIndicatorValue.age_end == data.age_end,
                indicator_models.DetailedIndicatorValue.year == request.year,
            )
        else:
            query = query.filter(
                indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
                indicator_models.DetailedIndicatorValue.territory_id == territory_id,
                indicator_models.DetailedIndicatorValue.age_start == data.age_start,
                indicator_models.DetailedIndicatorValue.age_end == data.age_end,
                indicator_models.DetailedIndicatorValue.year == request.year,
            )
        result = await db.execute(query)
        if result.scalars().all():
            query = (
                update(indicator_models.DetailedIndicatorValue)
                .where(
                    indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
                    indicator_models.DetailedIndicatorValue.age_start == data.age_start,
                    indicator_models.DetailedIndicatorValue.age_end == data.age_end,
                    indicator_models.DetailedIndicatorValue.year == request.year,
                )
                .values(male=data.male, female=data.female)
            )
            if oktmo:
                query = query.where(indicator_models.DetailedIndicatorValue.oktmo == oktmo)
            else:
                query = query.where(indicator_models.DetailedIndicatorValue.territory_id == territory_id)
            await db.execute(query)

        else:
            value = indicator_models.DetailedIndicatorValue(
                indicator_id=indicator_id,
                territory_id=territory_id,
                oktmo=oktmo,
                year=request.year,
                age_start=data.age_start,
                age_end=data.age_end,
                source=request.source,
                male=data.male,
                female=data.female,
            )

            db.add(value)
    await db.commit()

    return await get_detailed_indicator_values(db, indicator_id, territory_id, oktmo, year=request.year)
