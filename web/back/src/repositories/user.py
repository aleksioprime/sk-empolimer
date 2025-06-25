from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
import logging

from sqlalchemy import update, select
from sqlalchemy.exc import NoResultFound

from src.models.user import User
from src.repositories.base import BaseSQLRepository
from src.schemas.user import UserUpdateSchema, UserQueryParams

logger = logging.getLogger(__name__)

class BaseUserRepository(ABC):

    @abstractmethod
    async def update(self, user_id: UUID, body: UserUpdateSchema):
        ...


class UserRepository(BaseUserRepository, BaseSQLRepository):

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """
        Получает пользователя по его ID
        """
        query = select(User).filter(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalars().unique().one_or_none()

    async def get_user_all(self, params: UserQueryParams) -> List[User]:
        """ Получает список всех пользователей """
        query = (
            select(User)
            .limit(params.limit)
            .offset(params.offset)
        )
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def create(self, user: User) -> None:
        """ Добавляет нового пользователя в текущую сессию """
        self.session.add(user)

    async def update(self, user_id: UUID, body: UserUpdateSchema) -> User:
        """ Обновляет пользователя по его ID """
        update_data = {key: value for key, value in body.dict(exclude_unset=True).items()}
        if not update_data:
            raise NoResultFound("Нет данных для обновления")

        stmt = (
            update(User)
            .filter_by(id=user_id)
            .values(**update_data)
        )
        await self.session.execute(stmt)
        return await self.get_user_by_id(user_id)

    async def delete(self, user_id: UUID) -> None:
        """ Удаляет пользователя по его ID """
        result = await self.get_user_by_id(user_id)
        if not result:
            raise NoResultFound(f"Пользователь с ID {user_id} не найден")

        await self.session.delete(result)