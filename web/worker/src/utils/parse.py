from datetime import datetime, timezone


def parse_device_id(topic: str) -> str:
    """Извлекает device_id из MQTT-топика типа devices/<device_id>/air"""
    parts = topic.split('/')
    return parts[1] if len(parts) >= 3 else "unknown"


def parse_datetime(dt_str: str) -> datetime:
    """Парсит datetime из строки, возвращает timezone-aware UTC время"""
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.now(timezone.utc)