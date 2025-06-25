from typing import Generic, TypeVar, List

from fastapi import Query
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class BasePaginationParams(BaseModel):
    """ Базовый класс параметров пагинации """
    limit: int = Field(Query(alias='page_size', gt=0))
    offset: int = Field(Query(alias='page_number', ge=0))