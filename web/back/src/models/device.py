import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, String, Float, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.postgres import Base


ONLINE_INTERVAL = timedelta(minutes=5)


class Device(Base):
    """
    Модель устройства
    """
    __tablename__ = 'devices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String(255), nullable=True)

    data = relationship("DeviceData", back_populates="device")

    @property
    def last_data(self):
        """Последние данные от устройства"""
        return self.data.order_by(DeviceData.timestamp.desc()).first()

    @property
    def online(self):
        """Онлайн ли устройство (есть данные за последние N минут)"""
        last = self.last_data
        if not last:
            return False
        return (datetime.now(timezone.utc) - last.timestamp) < ONLINE_INTERVAL

    def __repr__(self) -> str:
        return f'<Device {self.name}>'


class DeviceData(Base):
    __tablename__ = 'device_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)

    device = relationship("Device", back_populates="data")

    def __repr__(self) -> str:
        return f'<DeviceData {self.device_id} @ {self.timestamp}: {self.temperature}°C, {self.humidity}%>'