from uuid import UUID
from typing import List

from sqlalchemy.exc import IntegrityError, NoResultFound

from src.exceptions.base import BaseException, NotFoundException
from src.models.device import Device
from src.repositories.uow import UnitOfWork
from src.schemas.device import DeviceSchema, DeviceUpdateSchema, DeviceDetailSchema


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

        return devices

    async def get_detail_by_id(self, device_id: UUID) -> DeviceDetailSchema:
        """
        Выдаёт детальную информацию об устройстве по его ID
        """
        async with self.uow:
            device = await self.uow.device.get_detail_by_id(device_id)

        if device is None:
            raise NotFoundException("Устройство не найдено")

        return device

    async def create(self, body: DeviceUpdateSchema) -> DeviceSchema:
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
                await self.uow.session.flush()
                device = await self.uow.device.get_detail_by_id(device.id)
            except IntegrityError as exc:
                raise BaseException("Устройство уже существует") from exc

        return DeviceSchema.model_validate(device)

    async def update(self, device_id: UUID, body: DeviceUpdateSchema) -> DeviceSchema:
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

        return DeviceSchema.model_validate(device)

    async def delete(self, device_id: UUID) -> None:
        """
        Удаляет устройство по его ID
        """
        async with self.uow:
            try:
                await self.uow.device.delete(device_id)
            except NoResultFound as exc:
                raise NotFoundException(f"Устройство с ID {device_id} не найдено") from exc