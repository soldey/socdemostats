from pydantic import BaseModel
from typing import List, Optional
from app.schemas.unit import UnitResponse
from app.models.base import metadata
from app.models.unit import Unit
from app.crud.unit import get_unit

# from sqlalchemy.ext.hybrid import hybrid_property


class IndicatorCreateRequest(BaseModel):
    name: str
    unit_id: int


class IndicatorShortDescriptionResponse(BaseModel):
    id: int
    name: str
    unit_name: str

    # @property
    # def unit(self) -> str:
    #     return self.unit.name

    # class Config:
    #     fields = {"unit": "_unit"}
    # class Config:
    #     from_attributes=True

    # class Config:
    #     table_source = {
    #         '_default': lambda name='indicators': metadata.tables.get(name),
    #         '_f_keys': {
    #             'unit': {
    #                 'table': lambda name='units': metadata.tables.get(name),
    #                 'model': Unit
    #             }
    #         }
    #     }


class IndicatorAvailability(BaseModel):
    year: int
    territory_id: Optional[int] = None
    source: str
    oktmo: Optional[int] = None


class IndicatorFullDescriptionResponse(BaseModel):
    id: int
    name: str
    unit: str
    detailed_availability: List[IndicatorAvailability]
    aggregated_availability: List[IndicatorAvailability]


class LoadIndicatorAggregatedRequest(BaseModel):
    year: int
    value: float
    source: str


class IndicatorAggregatedResponse(BaseModel):
    id: int
    indicator_id: int
    name: str
    unit: str
    territory_id: Optional[int] = None
    oktmo: Optional[int] = None
    year: int
    source: str
    value: float


class IndicatorDetailedData(BaseModel):
    age_start: int
    age_end: int | None
    male: Optional[float]
    female: Optional[float]


class LoadIndicatorDetailedRequest(BaseModel):
    year: int
    source: str
    data: List[IndicatorDetailedData]


class IndicatorDetailedResponse(BaseModel):
    indicator_id: int
    territory_id: Optional[int] = None
    oktmo: Optional[int] = None
    unit: str
    year: int
    source: str
    data: List[IndicatorDetailedData]

class IndicatorUniqueDetailedPair(BaseModel):
    year: int
    source: str
    
    def __hash__(self):
        return hash(self.year) + hash(self.source)
