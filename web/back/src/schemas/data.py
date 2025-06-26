from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.pagintation import BasePaginationParams


class DeviceDataQueryParams(BasePaginationParams):
    timestamp: datetime | None = Field(None, description="Дата/время полученных данных")

    class Config:
        arbitrary_types_allowed = True


class DeviceDataSchema(BaseModel):
    id: UUID = Field(..., description="ID полученных данных")
    timestamp: datetime = Field(..., description="Дата/время полученных данных")
    temperature: float = Field(..., description="Температура воздуха")
    humidity: float = Field(..., description="Влажность воздуха")

    class Config:
        from_attributes = True