"""
Модуль с эндпоинтами для управления пользователями
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from starlette import status

from src.schemas.security import UserJWT
from src.core.security import JWTBearer
from src.dependencies.user import get_user_service, get_user_params
from src.dependencies.security import role_required
from src.schemas.pagination import PaginatedResponse
from src.schemas.user import UserCreateSchema, UserUpdateSchema, UpdatePasswordUserSchema, UserSchema, UserQueryParams
from src.services.user import UserService

router = APIRouter()

@router.get(
    path='/',
    summary='Получить всех пользователей',
    response_model=PaginatedResponse[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
        params: Annotated[UserQueryParams, Depends(get_user_params)],
        service: Annotated[UserService, Depends(get_user_service)],
        user: Annotated[UserJWT, Depends(role_required(admin=True, superuser=True))],
) -> PaginatedResponse[UserSchema]:
    """
    Возвращает список всех пользователей
    """
    users = await service.get_user_all(params)
    return users

@router.get(
    path='/me/',
    summary='Получить информацию о себе',
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_me(
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
):
    """
    Возвращает информацию о текущем пользователе
    """
    user = await service.get_user_by_id(user.user_id)
    return user

@router.post(
    path='/',
    summary='Создаёт пользователя',
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def register(
        body: UserCreateSchema,
        service: Annotated[UserService, Depends(get_user_service)],
        user: Annotated[UserJWT, Depends(JWTBearer())],
) -> UserSchema:
    """
    Регистрирует нового пользователя.
    Зарегистрировать пользователя может только администратор
    """
    user: UserSchema = await service.create(body)
    return user

@router.patch(
    path='/{user_id}/',
    summary='Обновление пользователя',
    response_model=UserSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: UUID,
    body: UserUpdateSchema,
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
):
    """
    Обновляет информацию о пользователе
    """
    user = await service.update(user_id, body=body)
    return user

@router.delete(
    path='/{user_id}/',
    summary='Удаление пользователя',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserJWT, Depends(role_required(admin=True, superuser=True))],
):
    """
    Удаляет пользователя
    """
    await service.delete(user_id, user.user_id)

@router.patch(
    path='/{user_id}/reset-password/',
    summary='Обновление пароля пользователя',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_password_user(
    user_id: UUID,
    body: UpdatePasswordUserSchema,
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
):
    """
    Обновляет пароль пользователя
    """
    return await service.update_password(user_id, body=body)


@router.patch(
    path='/{user_id}/photo/',
    summary='Загрузить изображение пользователя',
    status_code=status.HTTP_200_OK,
)
async def upload_user_avatar(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
    photo: UploadFile = File(...),

):
    photo_url = await service.upload_photo(user_id, photo)
    return {"photo": photo_url}


@router.delete(
    path='/{user_id}/photo/',
    summary='Удалить фотографию пользователя',
    status_code=status.HTTP_200_OK,
)
async def delete_user_avatar(
    user_id: UUID,
    service: Annotated[UserService, Depends(get_user_service)],
    user: Annotated[UserJWT, Depends(JWTBearer())],
):
    """
    Удаляет фотографию пользователя
    """
    await service.delete_photo(user_id)
    return {"photo": None}