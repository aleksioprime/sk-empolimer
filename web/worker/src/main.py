import asyncio

from src.core.config import settings
from src.services.mqtt_worker import MQTTWorker


if __name__ == "__main__":
    worker = MQTTWorker(
        mqtt_broker=settings.mqtt.broker,
        mqtt_port=settings.mqtt.port,
        mqtt_topic=settings.mqtt.topic,
        mqtt_username=settings.mqtt.username,
        mqtt_password=settings.mqtt.password,
    )
    try:
        asyncio.run(worker.start())
    except KeyboardInterrupt:
        worker.stop()