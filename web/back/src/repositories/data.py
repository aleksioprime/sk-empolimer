from uuid import UUID
from typing import List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from src.models.device import DeviceData
from src.schemas.data import DeviceDataSchema, DeviceDataQueryParams, DeviceDataChartQueryParams, DeviceDataExportQueryParams

logger = logging.getLogger(__name__)


class DeviceDataRepository:
    """
    Репозиторий для работы с пациентами
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_device_with_count(self, device_id: UUID, params: DeviceDataQueryParams) -> tuple[list[DeviceDataSchema], int]:
        """ Возвращает постраничный список данных устройства и их общее количество """
        query = select(DeviceData).where(DeviceData.device_id == device_id)

        if params.start:
            query = query.where(DeviceData.timestamp >= params.start)
        if params.end:
            query = query.where(DeviceData.timestamp <= params.end)

        if params.field == "temperature":
            query = query.where(DeviceData.temperature != None)
        elif params.field == "humidity":
            query = query.where(DeviceData.humidity != None)

        total_query = select(func.count()).select_from(query.subquery())
        paginated_query = query.limit(params.limit).offset(params.offset * params.limit)

        total_result = await self.session.execute(total_query)
        result = await self.session.execute(paginated_query)

        total = total_result.scalar()
        items = result.scalars().unique().all()

        return items, total

    async def get_all_by_device(self, device_id: UUID, params: DeviceDataExportQueryParams) -> List[DeviceData]:
        """ Возвращает данные устойства по параметрам фильтра """
        query = select(DeviceData).where(DeviceData.device_id == device_id)
        if params.start:
            query = query.where(DeviceData.timestamp >= params.start)
        if params.end:
            query = query.where(DeviceData.timestamp <= params.end)
        if params.field == "temperature":
            query = query.where(DeviceData.temperature != None)
        elif params.field == "humidity":
            query = query.where(DeviceData.humidity != None)
        query = query.order_by(DeviceData.timestamp.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_by_device(self, device_id: UUID) -> None:
        """ Удаляет данные по ID устройства """
        stmt = delete(DeviceData).where(DeviceData.device_id == device_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def get_chart_data(self, device_id: UUID, params: DeviceDataChartQueryParams) -> list[DeviceData]:
        """
        Возвращает не более заданного количества точек данных для построения графика,
        равномерно распределяя их по периоду (без пропусков).
        """
        # 1. Формируем базовый запрос
        query = select(DeviceData).where(DeviceData.device_id == device_id)
        if params.start:
            query = query.where(DeviceData.timestamp >= params.start)
        if params.end:
            query = query.where(DeviceData.timestamp <= params.end)
        if params.field == "temperature":
            query = query.where(DeviceData.temperature != None)
        elif params.field == "humidity":
            query = query.where(DeviceData.humidity != None)
        query = query.order_by(DeviceData.timestamp.asc())

        # 2. Считаем всего точек в диапазоне
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # 3. Если точек <= limit — просто возвращаем все
        if total <= params.limit:
            result = await self.session.execute(query)
            return result.scalars().all()

        # 4. Если точек больше — берём только равномерно распределённые точки
        # Получаем индексы точек, которые нужны (например, [0, step, 2*step, ...])
        step = total / params.limit
        needed_indices = set(int(i * step) for i in range(params.limit))

        # 5. Запрашиваем только id-шники подходящих точек (например, row_number) — эффективно на больших выборках!
        subq = (
            select(
                DeviceData.id,
                func.row_number().over(order_by=DeviceData.timestamp.asc()).label("rn")
            )
            .where(DeviceData.device_id == device_id)
        )
        if params.start:
            subq = subq.where(DeviceData.timestamp >= params.start)
        if params.end:
            subq = subq.where(DeviceData.timestamp <= params.end)
        if params.field == "temperature":
            subq = subq.where(DeviceData.temperature != None)
        elif params.field == "humidity":
            subq = subq.where(DeviceData.humidity != None)

        subq = subq.order_by(DeviceData.timestamp.asc()).subquery()

        # Выбираем id только нужных row_number
        id_query = (
            select(subq.c.id)
            .where(subq.c.rn.in_([idx + 1 for idx in needed_indices]))
        )
        ids_result = await self.session.execute(id_query)
        ids = [row[0] for row in ids_result.all()]
        if not ids:
            return []

        # Итоговый запрос — только нужные точки
        data_query = select(DeviceData).where(DeviceData.id.in_(ids)).order_by(DeviceData.timestamp.asc())
        data_result = await self.session.execute(data_query)
        return data_result.scalars().all()