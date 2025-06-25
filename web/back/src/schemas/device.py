from __future__ import annotations

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class DeviceSchema(BaseModel):
    id: UUID = Field(..., description="Уникальный идентификатор устройства")
    name: str = Field(..., description="Название модели устройства")
    description: str | None = Field(None, description="Описание устройства")
    location: str | None = Field(None, description="Местоположение устройства")
    last_data: DeviceDataSchema | None = Field(None, description="Последние полученные данные устройства")

    class Config:
        from_attributes = True


class DeviceCreateSchema(BaseModel):
    name: str = Field(..., description="Название новой модели устройства")
    description: str | None = Field(None, description="Описание устройства")
    location: str | None = Field(None, description="Местоположение устройства")

class DeviceUpdateSchema(BaseModel):
    name: str | None = Field(None, description="Новое название устройства")
    description: str | None = Field(None, description="Новое описание устройства")
    location: str | None = Field(None, description="Новое местоположение устройства")


class DeviceDataSchema(BaseModel):
    id: UUID = Field(..., description="ID полученных данных")
    timestamp: datetime = Field(..., description="Дата/время полученных данных")
    temperature: float = Field(..., description="Температура воздуха")
    humidity: float = Field(..., description="Влажность воздуха")

    class Config:
        from_attributes = True


class DeviceDetailSchema(DeviceSchema):
    data: list[DeviceDataSchema] = Field(default_factory=list, description="Список данных, полученных устройством")


DeviceSchema.model_rebuild()