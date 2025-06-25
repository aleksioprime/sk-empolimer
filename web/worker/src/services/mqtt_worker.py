import asyncio
import json
import uuid

from aiomqtt import Client, MqttError
from sqlalchemy import select

from core.logger import logger
from src.db.postgres import session_factory
from src.models.device import DeviceData, Device
from src.utils.parse import parse_device_id, parse_datetime


class MQTTWorker:
    def __init__(self, mqtt_broker, mqtt_port, mqtt_topic, mqtt_username, mqtt_password):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self._should_run = True

    async def start(self):
        logger.info(f"MQTT worker запускается: {self.mqtt_broker}:{self.mqtt_port} / {self.mqtt_topic}")
        while self._should_run:
            try:
                async with Client(
                    hostname=self.mqtt_broker,
                    port=self.mqtt_port,
                    username=self.mqtt_username,
                    password=self.mqtt_password,
                ) as client:
                    await client.subscribe(self.mqtt_topic)
                    logger.info(f"Подписан на {self.mqtt_topic}")
                    async for message in client.messages:
                        # Если нужно — фильтруй по topic (например, если подписан на несколько)
                        # if message.topic.matches(self.mqtt_topic):
                        await self.process_message(message)
            except MqttError as e:
                logger.error(f"[MQTT ERROR] {e}. Переподключение через 5 сек...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"[WORKER ERROR] {e}")
                await asyncio.sleep(2)

    async def process_message(self, message):
        try:
            payload = json.loads(message.payload.decode())
            device_id = parse_device_id(message.topic.value)

            if not self.is_valid_uuid(device_id):
                logger.error(f"Неверный формат UUID device_id: {device_id}")
                return

            device_uuid = uuid.UUID(device_id)
            dt = parse_datetime(payload.get('datetime'))

            async with session_factory() as session:
                result = await session.execute(select(Device).where(Device.id == device_uuid))
                device = result.scalar()
                if not device:
                    logger.error(f"Устройство с таким UUID не найдено: {device_uuid}")
                    return

                data = DeviceData(
                    device_id=device_id,
                    timestamp=dt,
                    temperature=payload.get("temp"),
                    humidity=payload.get("hum"),
                )
                session.add(data)
                await session.commit()

                logger.info(
                    f"Данные сохранены: {device_id} {dt} t={payload.get('temp')} h={payload.get('hum')}"
                )
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")

    def stop(self):
        self._should_run = False

    def is_valid_uuid(self, val: str) -> bool:
        try:
            uuid.UUID(val)
            return True
        except Exception:
            return False
