from typing import Annotated, Literal
from datetime import datetime, date

from fastapi import Depends, Query

from src.schemas.pagination import BasePaginationParams
from src.schemas.data import DeviceDataQueryParams, DeviceDataChartQueryParams
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

def get_device_data_chart_params(
    start: datetime | None = Query(None, description="Начальная дата/время"),
    end: datetime | None = Query(None, description="Конечная дата/время"),
    field: Literal["temperature", "humidity"] | None = Query(None, description="Тип данных: температура или влажность"),
    limit: int = Query(100, description="Максимальное число точек на графике (по умолчанию 100)"),
) -> DeviceDataChartQueryParams:
    """Получает query-параметры фильтрации для данных для графика"""

    return DeviceDataChartQueryParams(
        start=start,
        end=end,
        field=field,
        limit=limit,
    )

def get_device_data_export_params(
    start: datetime | None = Query(None, description="Начальная дата/время"),
    end: datetime | None = Query(None, description="Конечная дата/время"),
    field: Literal["temperature", "humidity"] | None = Query(None, description="Тип данных: температура или влажность"),
) -> DeviceDataChartQueryParams:
    """Получает query-параметры фильтрации для данных для графика"""

    return DeviceDataChartQueryParams(
        start=start,
        end=end,
        field=field,
    )

def get_device_data_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> DeviceDataService:
    """
    Возвращает экземпляр DeviceDataService с переданным UnitOfWork (UoW)
    """
    return DeviceDataService(uow=uow)