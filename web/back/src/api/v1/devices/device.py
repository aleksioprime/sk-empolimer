from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from src.schemas.security import UserJWT
from src.core.security import JWTBearer
from src.dependencies.device import get_device_service
from src.schemas.device import DeviceSchema, DeviceCreateSchema, DeviceUpdateSchema, DeviceEditSchema, DeviceDetailSchema
from src.services.device import DeviceService


router = APIRouter()

@router.get(
    path='/',
    summary='Получить все устройства',
    response_model=list[DeviceSchema],
    status_code=status.HTTP_200_OK,
)
async def get_devices(
        service: Annotated[DeviceService, Depends(get_device_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> list[DeviceSchema]:
    """
    Возвращает список всех устройств
    """
    devices = await service.get_all()
    return devices


@router.get(
    path='/{device_id}/',
    summary='Получить детальную информацию об устройстве',
    response_model=DeviceDetailSchema,
    status_code=status.HTTP_200_OK,
)
async def get_device(
        device_id: UUID,
        service: Annotated[DeviceService, Depends(get_device_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> DeviceDetailSchema:
    """
    Получает детальную информацию об устройстве
    """
    device = await service.get_detail_by_id(device_id)
    return device


@router.post(
    path='/',
    summary='Создаёт устройство',
    response_model=DeviceEditSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
        body: DeviceCreateSchema,
        service: Annotated[DeviceService, Depends(get_device_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> DeviceEditSchema:
    """
    Создаёт новое устройство
    """
    device = await service.create(body)
    return device


@router.patch(
    path='/{device_id}/',
    summary='Обновляет устройство',
    response_model=DeviceEditSchema,
    status_code=status.HTTP_200_OK,
)
async def update_device(
        device_id: UUID,
        body: DeviceUpdateSchema,
        service: Annotated[DeviceService, Depends(get_device_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> DeviceEditSchema:
    """
    Обновляет устройство по его ID
    """
    device = await service.update(device_id, body)
    return device


@router.delete(
    path='/{device_id}/',
    summary='Удаляет устройство',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_device(
        device_id: UUID,
        service: Annotated[DeviceService, Depends(get_device_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> None:
    """
    Удаляет устройство по его ID
    """
    await service.delete(device_id)