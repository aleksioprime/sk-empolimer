import logging

from fastapi import WebSocket
from typing import List

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        logger.info(f"[WS-Manager] CONNECTED: {websocket.client} (Total: {len(self.connections)})")

    async def broadcast(self, data: str):
        for connection in self.connections:
            await connection.send_text(data)


manager = ConnectionManager()