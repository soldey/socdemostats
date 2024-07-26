from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
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
        {"year": row.year, "territory_id": row.territory_id, "source": row.source} for row in result.scalars().all()
    ]


async def get_detailed_indicator_values_availability(db: AsyncSession, indicator_id: int):
    result = await db.execute(
        select(indicator_models.DetailedIndicatorValue).filter(
            indicator_models.DetailedIndicatorValue.indicator_id == indicator_id
        )
    )

    return [
        {"year": row.year, "territory_id": row.territory_id, "source": row.source} for row in result.scalars().all()
    ]


async def create_aggregated_indicator_values(
    db: AsyncSession,
    indicator_id: int,
    territory_id: int,
    indicator_values: list[schemas.LoadIndicatorAggregatedRequest],
):
    # indicator = await get_indicator(db, indicator_id)
    for indicator_value in indicator_values:
        query = select(indicator_models.AggregatedIndicatorValue).where(
            indicator_models.AggregatedIndicatorValue.indicator_id == indicator_id,
            indicator_models.AggregatedIndicatorValue.territory_id == territory_id,
            indicator_models.AggregatedIndicatorValue.year == indicator_value.year,
        )
        result = await db.execute(query)
        if result.scalars().all():
            await db.execute(
                update(indicator_models.AggregatedIndicatorValue)
                .where(
                    indicator_models.AggregatedIndicatorValue.indicator_id == indicator_id,
                    indicator_models.AggregatedIndicatorValue.territory_id == territory_id,
                    indicator_models.AggregatedIndicatorValue.year == indicator_value.year,
                )
                .values(value=indicator_value.value, source=indicator_value.source)
            )
        else:
            db_indicator_aggregated_value = indicator_models.AggregatedIndicatorValue(
                indicator_id=indicator_id,
                territory_id=territory_id,
                year=indicator_value.year,
                value=indicator_value.value,
                source=indicator_value.source,
            )
            db.add(db_indicator_aggregated_value)
    await db.commit()


async def get_aggregated_indicator_values(db: AsyncSession, indicator_id: int, territory_id: int, year: int = None):
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
    result = await db.execute(query)
    return result.scalars().all()


async def get_detailed_indicator_values(
    db: AsyncSession, indicator_id: int, territory_id: int, year: int | None = None
) -> list[schemas.IndicatorDetailedResponse] | None:
    query = (
        select(indicator_models.DetailedIndicatorValue)
        .options(joinedload(indicator_models.DetailedIndicatorValue.indicator))
        .filter(
            indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
            indicator_models.DetailedIndicatorValue.territory_id == territory_id,
        )
        .order_by(indicator_models.DetailedIndicatorValue.age_start)
    )

    if year is not None:
        query = query.filter(indicator_models.DetailedIndicatorValue.year == year)

    result = await db.execute(query)
    values = result.scalars().all()

    if not values:
        return None

    # Group by year if year is None
    values_by_year: dict[int, list[schemas.DetailedIndicatorValue]] = {}
    for value in values:
        if value.year not in values_by_year:
            values_by_year[value.year] = []
        values_by_year[value.year].append(value)

    responses = []
    for year, values in values_by_year.items():
        first_value = values[0]
        unit = await first_value.indicator.awaitable_attrs.unit
        response = schemas.IndicatorDetailedResponse(
            indicator_id=first_value.indicator_id,
            territory_id=first_value.territory_id,
            unit=unit.unit_name,
            year=year,
            source=first_value.source,
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
    db: AsyncSession, indicator_id: int, territory_id: int, request: schemas.LoadIndicatorDetailedRequest
) -> list[indicator_models.DetailedIndicatorValue]:
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
        result = await db.execute(query)
        if result.scalars().all():
            await db.execute(
                update(indicator_models.DetailedIndicatorValue)
                .where(
                    indicator_models.DetailedIndicatorValue.indicator_id == indicator_id,
                    indicator_models.DetailedIndicatorValue.territory_id == territory_id,
                    indicator_models.DetailedIndicatorValue.age_start == data.age_start,
                    indicator_models.DetailedIndicatorValue.age_end == data.age_end,
                    indicator_models.DetailedIndicatorValue.year == request.year,
                )
                .values(male=data.male, female=data.female)
            )

        else:
            value = indicator_models.DetailedIndicatorValue(
                indicator_id=indicator_id,
                territory_id=territory_id,
                year=request.year,
                age_start=data.age_start,
                age_end=data.age_end,
                source=request.source,
                male=data.male,
                female=data.female,
            )

            db.add(value)
    await db.commit()

    return await get_detailed_indicator_values(db, indicator_id, territory_id, year=request.year)
