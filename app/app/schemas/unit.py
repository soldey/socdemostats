from pydantic import BaseModel

class UnitCreateRequest(BaseModel):
    unit_name: str

class UnitResponse(BaseModel):
    id: int
    unit_name: str

    class Config:
        orm_mode: True