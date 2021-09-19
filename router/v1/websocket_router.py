import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, DefaultDict, Any

from fastapi import WebSocket, WebSocketDisconnect, FastAPI, Header
from fastapi.responses import JSONResponse
from loguru import logger

from application.play import RoomPlay
from application.instruct_executor import instruct_map, instruct_executor
from service.user_service import check_room_token_can_join
from utils.const_utils import SystemConst, RoomConst

socket_router = FastAPI()
room_pool = {}

process_pool = ThreadPoolExecutor(max_workers=4)


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
            if client_id in self.client_user_map:
                message.update({
                    'user_name': self.client_user_map[client_id]['user_name']
                })
        for connection in self.active_connections[room_id].values():
            await connection.send_json(message)
            logger.debug(message)


manager = ConnectionManager()


@socket_router.get('/')
async def test():
    return "success"


@socket_router.websocket("/conn/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int,
                             client_id: str = Header(None, convert_underscores=False)):
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
            if data.get('chat'):
                if data.get('say'):
                    await manager.broadcast({'client_id': client_id, 'say': data['say']}, room_id)
            if data.get('system'):
                if data.get('instruct') == SystemConst.ACTION_START and user['room_owner']:
                    if room_pool.get(room_id) not in {RoomConst.STATUS_GAMING, RoomConst.STATUS_CLOSED}:
                        rp = RoomPlay(room_id, manager.broadcast)
                        room_pool.update({room_id: rp})
                        room_pool[room_id].status = RoomConst.STATUS_GAMING
                        for i in reversed(range(1, 6)):
                            await manager.broadcast({'message': f'房间{room_id}开始游戏， 倒计时{i}'}, room_id)
                            await asyncio.sleep(1)
                        process_pool.submit(run, room_id)
                    else:
                        await manager.send_personal_message({'message': '不能重复开始游戏！！！'}, websocket)

                if data.get('help'):
                    await manager.send_personal_message(instruct_map, websocket)
            if data.get('game'):
                # 将玩家str指令转换为具体游戏逻辑, 如: {"instruct": "take_coin", "coin_list": ["红色", "蓝色", "白色"]}
                instruct_executor.execute(room_id, data)

    except WebSocketDisconnect:
        manager.disconnect(room_id, client_id)
        await manager.broadcast({'client_id': client_id, 'system': 'disconnect'}, room_id)


def run(room_id):
    asyncio.run(room_pool[room_id].runtime_process())
