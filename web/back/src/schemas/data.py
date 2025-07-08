from uuid import UUID
from typing import Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.pagination import BasePaginationParams


class DeviceDataQueryParams(BasePaginationParams):
    start: Optional[datetime] = Field(None, description="Начальная дата/время")
    end: Optional[datetime] = Field(None, description="Конечная дата/время")
    field: Optional[Literal["temperature", "humidity"]] = Field(
        None, description="Тип данных: температура или влажность"
    )

    class Config:
        arbitrary_types_allowed = True


class DeviceDataSchema(BaseModel):
    id: UUID = Field(..., description="ID полученных данных")
    timestamp: datetime = Field(..., description="Дата/время полученных данных")
    temperature: float = Field(..., description="Температура воздуха")
    humidity: float = Field(..., description="Влажность воздуха")
    battery: float | None = Field(None, description="Заряд аккумулятора")

    class Config:
        from_attributes = True


class DeviceDataDeleteResponse(BaseModel):
    device_id: UUID = Field(..., description="ID устройства")
    deleted_count: int = Field(..., description="Кол-во удалённых данных")


class DeviceDataChartQueryParams(BaseModel):
    start: datetime | None = Field(None, description="Начальная дата/время")
    end: datetime | None = Field(None, description="Конечная дата/время")
    field: Literal["temperature", "humidity"] | None = Field(
        None, description="Тип данных: температура или влажность"
    )
    limit: int = Field(100, description="Максимальное число точек на графике (по умолчанию 100)")

    class Config:
        arbitrary_types_allowed = True

class DeviceDataExportQueryParams(BaseModel):
    start: datetime | None = Field(None, description="Начальная дата/время")
    end: datetime | None = Field(None, description="Конечная дата/время")
    field: Literal["temperature", "humidity"] | None = Field(
        None, description="Тип данных: температура или влажность"
    )

    class Config:
        arbitrary_types_allowed = True