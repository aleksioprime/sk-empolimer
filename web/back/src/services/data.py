from uuid import UUID
from typing import List
from io import BytesIO
import logging

from openpyxl import Workbook
from sqlalchemy.exc import NoResultFound

from src.exceptions.base import NotFoundException
from src.schemas.pagintation import PaginatedResponse
from src.schemas.data import DeviceDataSchema, DeviceDataQueryParams, DeviceDataChartQueryParams, DeviceDataExportQueryParams, DeviceDataDeleteResponse
from src.repositories.uow import UnitOfWork

logger = logging.getLogger(__name__)


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

    async def delete_by_device(self, device_id: UUID) -> DeviceDataDeleteResponse:
        """
        Удаляет данные по ID устройства. Возвращает объект с device_id и количеством удалённых записей.
        """
        async with self.uow:
            try:
                deleted_count = await self.uow.data.delete_by_device(device_id)
                return DeviceDataDeleteResponse(device_id=device_id, deleted_count=deleted_count)
            except NoResultFound as exc:
                raise NotFoundException(f"Данные устройства с ID {device_id} не найдены") from exc

    async def get_chart_data(self, device_id: UUID, params: DeviceDataChartQueryParams) -> list[DeviceDataSchema]:
        """
        Получает данные для графика по периоду с лимитом по количеству точек
        """
        async with self.uow:
            result = await self.uow.data.get_chart_data(device_id, params)
            return [DeviceDataSchema.model_validate(row) for row in result]

    async def export_to_excel(self, device_id: UUID, params: DeviceDataExportQueryParams) -> bytes:
        """
        Формирует файл excel с данными устройства
        """
        async with self.uow:
            data = await self.uow.data.get_all_by_device(device_id, params)

        wb = Workbook()
        ws = wb.active
        ws.title = "Device Data"

        # Заголовки
        headers = ["ID", "Дата/время", "Температура", "Влажность", "Заряд батареи"]
        ws.append(headers)

        for row in data:
            ws.append([
                str(row.id),
                row.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                row.temperature,
                row.humidity,
                row.battery,
            ])

        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.read()