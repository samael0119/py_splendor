import json
from collections import defaultdict
from typing import Dict, DefaultDict, Any

from fastapi import WebSocket, WebSocketDisconnect, FastAPI, Header
from fastapi.responses import JSONResponse
from loguru import logger

from application.play import play
from service.user_service import check_room_token_can_join
from utils.const_utils import SystemConst

socket_router = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: DefaultDict[Any, Dict[Any, WebSocket]] = defaultdict(dict)
        self.client_user_map = {}
        # self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, room_id: int, client_id: str, user: dict):
        await websocket.accept()
        self.active_connections[room_id][client_id] = websocket
        self.client_user_map[client_id] = user

    def disconnect(self, room_id, client_id):
        del self.active_connections[room_id][client_id]
        del self.client_user_map[client_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
        logger.info(message)

    async def broadcast(self, message: dict, room_id):
        message.update({
            'room_id': room_id
        })
        if 'client_id' in message:
            client_id = message.pop('client_id')
            message.update({
                'user_name': self.client_user_map[client_id]['user_name']
            })
        for connection in self.active_connections[room_id].values():
            await connection.send_json(message)
            logger.info(message)


manager = ConnectionManager()


@socket_router.get('/')
async def test():
    return "success"


@socket_router.websocket("/conn/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, client_id: str = Header(None, convert_underscores=False)):
    # check user_token
    user = check_room_token_can_join(room_id, client_id)
    if not user:
        # ERROR: ASGI callable returned without sending handshake.
        # must close!!!
        await websocket.close()
        return JSONResponse(content={'message': 'client_id unknown', 'data': None}, status_code=403)
    await manager.connect(websocket, room_id, client_id, user)
    try:
        while True:
            data = await websocket.receive_json()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            if 'say' in data:
                await manager.broadcast({'client_id': client_id, 'say': data['say']}, room_id)
            if 'system' in data and data['system'] == SystemConst.ACTION_START and user['room_owner']:
                await play(room_id)
    except WebSocketDisconnect:
        manager.disconnect(room_id, client_id)
        await manager.broadcast({'client_id': client_id, 'system': 'disconnect'}, room_id)
