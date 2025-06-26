import asyncio
import logging
import json

from src.managers.ws import manager
from src.dependencies.device import get_device_service
from src.dependencies.uow import get_unit_of_work
from src.schemas.device import DeviceSchema

logger = logging.getLogger(__name__)

async def periodic_broadcast():
    while True:
        try:
            if not manager.connections:
                await asyncio.sleep(1)
                continue

            service = await get_device_service(uow=await get_unit_of_work())
            devices = await service.get_all()
            payload = {
                "type": "devices_update",
                "devices": [DeviceSchema.model_validate(obj).model_dump(mode="json") for obj in devices]
            }
            await manager.broadcast(json.dumps(payload))
            # logger.info(f"[WS] Отправляем payload размером {len(devices)} устройств")
        except Exception as e:
            logger.error(f"WebSocket periodic broadcast error: {e}")
        await asyncio.sleep(5)
