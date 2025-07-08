from typing import Annotated
from uuid import UUID
from io import BytesIO
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from starlette import status

from src.schemas.security import UserJWT
from src.schemas.pagination import PaginatedResponse
from src.core.security import JWTBearer
from src.dependencies.data import get_device_data_params, get_device_data_service, get_device_data_chart_params, get_device_data_export_params
from src.schemas.data import DeviceDataSchema, DeviceDataQueryParams, DeviceDataChartQueryParams, DeviceDataExportQueryParams, DeviceDataDeleteResponse
from src.services.data import DeviceDataService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    path='/',
    summary='Получить все данные заданного устройства',
    response_model=PaginatedResponse[DeviceDataSchema],
    status_code=status.HTTP_200_OK,
)
async def get_data_by_devices(
        device_id: UUID,
        params: Annotated[DeviceDataQueryParams, Depends(get_device_data_params)],
        service: Annotated[DeviceDataService, Depends(get_device_data_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> list[DeviceDataSchema]:
    """
    Возвращает список всех устройств
    """
    datas = await service.get_by_device(device_id, params)
    return datas


@router.get(
    path="/chart/",
    summary="Данные для графика устройства (агрегированные)",
    response_model=list[DeviceDataSchema],
    status_code=status.HTTP_200_OK,
)
async def get_device_chart_data(
    device_id: UUID,
    params: Annotated[DeviceDataChartQueryParams, Depends(get_device_data_chart_params)],
    service: Annotated[DeviceDataService, Depends(get_device_data_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
) -> list[DeviceDataSchema]:
    """
    Данные для построения графика по устройству, равномерно агрегированные.
    """
    datas = await service.get_chart_data(device_id, params)
    return datas


@router.delete(
        path="/",
        summary='Удалить все данные заданного устройства',
        response_model=DeviceDataDeleteResponse,
        status_code=status.HTTP_200_OK,
        )
async def delete_device_data(
    device_id: UUID,
    service: Annotated[DeviceDataService, Depends(get_device_data_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
) -> DeviceDataDeleteResponse:
    return await service.delete_by_device(device_id)


@router.get(
    "/export/",
    summary="Скачать данные устройства в формате Excel",
    response_class=StreamingResponse,
)
async def export_device_data_to_excel(
    device_id: UUID,
    params: Annotated[DeviceDataExportQueryParams, Depends(get_device_data_export_params)],
    service: Annotated[DeviceDataService, Depends(get_device_data_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
):
    """
    Скачать все данные устройства в формате Excel
    """
    logger.info(f"Параметры: {params}")
    file_bytes = await service.export_to_excel(device_id, params)
    filename = f"device_data.xlsx"
    return StreamingResponse(
        BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )