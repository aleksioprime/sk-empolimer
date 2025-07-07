from uuid import UUID

from pydantic import BaseModel, Field


class AuthSchema(BaseModel):
    """
    Схема для аутентификации пользователя.
    Определяет поля, необходимые для входа в систему
    """

    username: str = Field(..., description="Логин пользователя")
    password: str = Field(..., description="Пароль пользователя")


class UserJWT(BaseModel):
    """
    Схема для представления данных пользователя в JWT
    """
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    is_superuser: bool = False
    is_admin: bool = False