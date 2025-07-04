from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, func
from sqlalchemy.orm import aliased
from sqlalchemy.exc import NoResultFound

from src.models.device import Device, DeviceData
from src.schemas.device import DeviceUpdateSchema


class DeviceRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[tuple[Device, DeviceData | None]]:
        """
        Получает все устройства + их последние данные одним запросом через оконные функции
        """
        DeviceDataAlias = aliased(DeviceData)

        # Оконная функция для поиска самой последней записи по device_id
        row_number = func.row_number().over(
            partition_by=DeviceData.device_id,
            order_by=DeviceData.timestamp.desc()
        ).label("row_number")

        data_subquery = (
            select(
                DeviceData,
                row_number
            )
            .subquery()
        )

        # Соединяем устройства и их last_data (row_number == 1)
        stmt = (
            select(Device, DeviceDataAlias)
            .outerjoin(
                data_subquery,
                (Device.id == data_subquery.c.device_id) & (data_subquery.c.row_number == 1)
            )
            .outerjoin(DeviceDataAlias, DeviceDataAlias.id == data_subquery.c.id)
            .order_by(Device.name)
        )

        result = await self.session.execute(stmt)
        return result.all()

    async def get_detail_by_id(self, device_id: UUID, data_limit: int = 24) -> tuple[Optional[Device], List[Optional[DeviceData]]]:
        """
        Получает детальную информацию об устройстве по его ID и равномерно распределённые данные за последние сутки.
        """
        query = select(Device).where(Device.id == device_id)
        result = await self.session.execute(query)
        device = result.scalar_one_or_none()

        if not device:
            return None, []

        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        interval = timedelta(seconds=(24 * 60 * 60) // data_limit)  # шаг между точками

        # 1. Получить все записи за сутки
        data_query = (
            select(DeviceData)
            .where(
                DeviceData.device_id == device_id,
                DeviceData.timestamp >= yesterday,
                DeviceData.timestamp <= now
            )
            .order_by(DeviceData.timestamp.asc())
        )
        data_result = await self.session.execute(data_query)
        all_data = data_result.scalars().all()

        # 2. Для каждого интервала брать ближайшую к центру запись (или None)
        points = []
        for i in range(data_limit):
            interval_start = yesterday + i * interval
            interval_end = interval_start + interval
            interval_center = interval_start + (interval / 2)
            # Найти запись в интервале, ближайшую к центру
            candidates = [
                d for d in all_data
                if interval_start <= d.timestamp < interval_end
            ]
            if candidates:
                # Найдём ближайшую к центру
                closest = min(candidates, key=lambda d: abs(d.timestamp - interval_center))
                points.append(closest)

        return device, points

    async def create(self, device: Device) -> None:
        """ Создаёт новое устройство """
        self.session.add(device)
        await self.session.flush()

    async def update(self, device_id: UUID, body: DeviceUpdateSchema) -> Device:
        """ Обновляет устройство по его ID """
        update_data = {k: v for k, v in body.dict(exclude_unset=True).items()}
        if not update_data:
            raise NoResultFound("Нет данных для обновления")

        stmt = (
            update(Device)
            .where(Device.id == device_id)
            .values(**update_data)
        )
        await self.session.execute(stmt)
        return await self._get_by_id(device_id)

    async def delete(self, device_id: UUID) -> None:
        """ Удаляет устройство по его ID """
        result = await self._get_by_id(device_id)
        if not result:
            raise NoResultFound(f"Устройство с ID {device_id} не найдено")

        await self.session.delete(result)

    async def _get_by_id(self, device_id: UUID) -> Device:
        """ Получает устройство по его ID """
        query = select(Device).where(Device.id == device_id)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()