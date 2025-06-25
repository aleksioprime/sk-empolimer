from pydantic import Field
from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    """
    Конфигурация для настроек базы данных
    """

    name: str = Field(alias='DB_NAME', default='database')
    user: str = Field(alias='DB_USER', default='admin')
    password: str = Field(alias='DB_PASSWORD', default='123qwe')
    host: str = Field(alias='DB_HOST', default='127.0.0.1')
    port: int = Field(alias='DB_PORT', default=5432)
    show_query: bool = Field(alias='SHOW_SQL_QUERY', default=False)

    @property
    def _base_url(self) -> str:
        """ Формирует базовый URL для подключения к базе данных """
        return f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def dsn(self) -> str:
        """ Формирует DSN строку для подключения к базе данных с использованием asyncpg """
        return f"postgresql+asyncpg://{self._base_url}"


class MQTTSettings(BaseSettings):
    """
    Конфигурация для настроек MQTT-брокера
    """

    broker: str = Field(alias='MQTT_BROKER', default='mqtt')
    port: int = Field(alias='MQTT_PORT', default=1883)
    username: str = Field(alias='MQTT_USERNAME', default='username')
    password: str = Field(alias='MQTT_PASSWORD', default='password')
    topic: str = Field(alias='MQTT_TOPIC', default='devices/+/air')


class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    mqtt: MQTTSettings = MQTTSettings()


settings = Settings()
