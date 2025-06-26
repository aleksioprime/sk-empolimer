from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette import status

from src.managers.ws import manager
from src.core.security import JWTBearer

router = APIRouter()

jwt_bearer = JWTBearer(auto_error=False)


@router.websocket("/ws/")
async def websocket_devices(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user = None
    if token:
        user = JWTBearer.parse_token(token)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect as e:
        manager.connections.remove(websocket)
