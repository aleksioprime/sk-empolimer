from typing import Annotated
from datetime import datetime, date

from fastapi import Depends, Query

from src.schemas.pagintation import BasePaginationParams
from src.schemas.data import DeviceDataQueryParams
from src.dependencies.pagination import get_pagination_params
from src.dependencies.uow import get_unit_of_work
from src.repositories.uow import UnitOfWork
from src.services.data import DeviceDataService


def get_device_data_params(
        pagination: Annotated[BasePaginationParams, Depends(get_pagination_params)],
        timestamp: datetime | None = Query(None, description='Параметр фильтрации по дате и времени'),
) -> DeviceDataQueryParams:
    """ Получает query-параметры фильтрации для данных """

    return DeviceDataQueryParams(
        limit=pagination.limit,
        offset=pagination.offset,
        timestamp=timestamp,
    )

def get_device_data_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> DeviceDataService:
    """
    Возвращает экземпляр DeviceDataService с переданным UnitOfWork (UoW)
    """
    return DeviceDataService(uow=uow)