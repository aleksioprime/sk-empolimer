from uuid import UUID
from typing import List
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.base import BaseException, NotFoundException
from src.models.device import Device
from src.repositories.uow import UnitOfWork
from src.schemas.device import DeviceSchema, DeviceUpdateSchema, DeviceDetailSchema, DeviceEditSchema, DeviceDataSchema


ONLINE_INTERVAL = timedelta(minutes=5)

class DeviceService:
    """
    Сервис для управления устройствами
    """
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all(self) -> List[DeviceSchema]:
        """
        Выдаёт список всех устройств
        """
        async with self.uow:
            devices = await self.uow.device.get_all()

        result = []
        now = datetime.now(timezone.utc)
        for device, last_data in devices:
            is_online = (
                last_data is not None and
                (now - last_data.timestamp) < ONLINE_INTERVAL
            )
            result.append(
                DeviceSchema(
                    **device.__dict__,
                    last_data=DeviceDataSchema.model_validate(last_data) if last_data else None,
                    online=is_online
                )
            )
        return result

    async def get_detail_by_id(self, device_id: UUID, data_limit: int = 10) -> DeviceDetailSchema:
        """
        Выдаёт детальную информацию об устройстве по его ID
        """
        async with self.uow:
            device, last_data = await self.uow.device.get_detail_by_id(device_id, data_limit=data_limit)

        if device is None:
            raise NotFoundException("Устройство не найдено")

        # Формируем единую схему для ответа (Pydantic)
        return DeviceDetailSchema(
            **device.__dict__,
            data=[DeviceDataSchema.model_validate(d) for d in last_data]
        )

    async def create(self, body: DeviceUpdateSchema) -> DeviceEditSchema:
        """
        Создаёт новое устройство
        """
        async with self.uow:
            try:
                device = Device(
                    name=body.name,
                    description=body.description,
                    location=body.location,
                )
                await self.uow.device.create(device)
            except IntegrityError as exc:
                raise BaseException("Устройство уже существует") from exc

        return DeviceEditSchema.model_validate(device)

    async def update(self, device_id: UUID, body: DeviceUpdateSchema) -> DeviceEditSchema:
        """
        Обновляет информацию об устройстве по его ID
        """
        async with self.uow:
            try:
                device = await self.uow.device.update(device_id, body)
                if device is None:
                    raise NotFoundException(f"Устройство с ID {device_id} не найдено")
            except NoResultFound as exc:
                raise NotFoundException(f"Устройство с ID {device_id} не найдено") from exc
            except IntegrityError as exc:
                raise BaseException("Устройство уже существует") from exc

        return DeviceEditSchema.model_validate(device)

    async def delete(self, device_id: UUID) -> None:
        """
        Удаляет устройство по его ID
        """
        async with self.uow:
            try:
                await self.uow.device.delete(device_id)
            except NoResultFound as exc:
                raise NotFoundException(f"Устройство с ID {device_id} не найдено") from exc