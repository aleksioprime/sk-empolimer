from uuid import UUID
from typing import List

from sqlalchemy.exc import IntegrityError

from src.models.user import User
from src.repositories.uow import UnitOfWork
from src.schemas.user import UserCreateSchema, UserUpdateSchema, UserSchema, UserQueryParams
from src.exceptions.base import BaseException


class UserService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_user_all(self, params: UserQueryParams) -> List[UserSchema]:
        """
        Выдаёт информацию обо всех пользователях
        """
        async with self.uow:
            users = await self.uow.user.get_user_all(params)

        return users

    async def get_user_by_id(self, user_id: UUID) -> UserSchema:
        """
        Выдаёт информацию о пользователе по его ID
        """
        async with self.uow:
            user = await self.uow.user.get_user_by_id(user_id)
            if not user:
                raise BaseException(f"Пользователь с ID {user_id} не найден")
        return user

    async def create(self, body: UserCreateSchema) -> User:
        """
        Создаёт пользователя
        """
        async with self.uow:
            try:
                user = User(
                    username=body.username,
                    password=body.password,
                    email=body.email,
                    first_name=body.first_name,
                    last_name=body.last_name,
                )

                await self.uow.user.create(user)
            except IntegrityError as e:
                raise BaseException("Пользователь уже существует") from e

        return user

    async def update(self, user_id: UUID, body: UserUpdateSchema) -> UserSchema:
        """
        Обновляет информацию о пользователе
        """
        async with self.uow:
            user = await self.uow.user.update(user_id, body)
        return user

    async def delete(self, user_id: UUID, auth_user_id: UUID) -> None:
        """
        Удаляет пользователя из базы данных
        """
        if user_id == auth_user_id:
            raise BaseException("Нельзя удалить самого себя")

        async with self.uow:
            await self.uow.user.delete(user_id)
