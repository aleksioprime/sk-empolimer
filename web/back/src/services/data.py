from uuid import UUID
from typing import List


from src.schemas.pagintation import PaginatedResponse
from src.schemas.data import DeviceDataSchema, DeviceDataQueryParams
from src.repositories.uow import UnitOfWork


class DeviceDataService:
    """ Сервис для управления данными устройства """
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_by_device(self, device_id: UUID, params: DeviceDataQueryParams) -> List[DeviceDataSchema]:
        """
        Выдаёт список данных с конкретного устройства
        """
        async with self.uow:
            datas, total = await self.uow.data.get_by_device_with_count(device_id, params)

        return PaginatedResponse[DeviceDataSchema](
            items=datas,
            total=total,
            limit=params.limit,
            offset=params.offset,
            has_next=(params.offset + 1) * params.limit < total,
            has_previous=params.offset > 0
        )