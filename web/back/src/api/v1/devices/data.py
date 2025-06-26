from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.schemas.security import UserJWT
from src.schemas.pagintation import PaginatedResponse
from src.core.security import JWTBearer
from src.dependencies.data import get_device_data_params, get_device_data_service
from src.schemas.data import DeviceDataSchema, DeviceDataQueryParams
from src.services.data import DeviceDataService


router = APIRouter()

@router.get(
    path='/',
    summary='Получить все данные заданного устройства',
    response_model=PaginatedResponse[DeviceDataSchema],
    status_code=status.HTTP_200_OK,
)
async def get_devices(
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