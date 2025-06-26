from uuid import UUID
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models.device import DeviceData
from src.schemas.data import DeviceDataSchema, DeviceDataQueryParams


class DeviceDataRepository:
    """
    Репозиторий для работы с пациентами
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_device_with_count(self, device_id: UUID, params: DeviceDataQueryParams) -> tuple[list[DeviceDataSchema], int]:
        """ Возвращает постраничный список пациентов и их общее количество """
        query = select(DeviceData).where(DeviceData.device_id == device_id)

        if params.timestamp:
            query = query.where(DeviceData.timestamp == params.timestamp)

        total_query = select(func.count()).select_from(query.subquery())

        paginated_query = query.limit(params.limit).offset(params.offset * params.limit)

        total_result = await self.session.execute(total_query)
        result = await self.session.execute(paginated_query)

        total = total_result.scalar()
        items = result.scalars().unique().all()

        return items, total