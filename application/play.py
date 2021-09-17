import asyncio
import json
import time

from model.game import RoomSummary
from model.user import Player
from router.v1 import websocket_router
from service.game_service import game_resource_init, roll_first_action_player, get_room_info, set_room_info, \
    get_room_player_list
from service.user_service import set_player_info, wait_player_action, get_player_info_by_room_user_id_list, \
    get_player_info_by_id
from utils.const_utils import ServiceCode, RoomConst, UserConst


class RoomPlay:
    status = RoomConst.STATUS_WAITING
    action_sleep = 1

    def __init__(self, room_id, broadcast):
        self._room_id = room_id
        self._broadcast = broadcast
        # get_room_info
        self._room = get_room_info(self._room_id)
        # check room status
        # if room.room_status != RoomConst.STATUS_WAITING:
        #     logger.info("房间状态不为等待中，开始失败")
        #     return False

        # check player ready status

        # set_room_status, room_user_status
        res = set_room_info(self._room_id, {RoomSummary.room_status: RoomConst.STATUS_GAMING})
        if res != ServiceCode.SUCCESS:
            raise Exception('房间状态改变失败')

        # init game
        self.card_resource, self.coin_resource = game_resource_init(self._room.card_summary_id,
                                                                    self._room.coin_summary_id,
                                                                    self._room.max_player)

        # add to redis
        # redis_conn = RedisConnector().get_conn()

        # roll first player
        self._room_user_list = get_room_player_list(self._room_id)
        self._room_user_token = {item.id: item.user_client_token for item in self._room_user_list}
        self._user_seat_num_dict = {n.id: n.seat_num for n in self._room_user_list}
        self._player_list = sorted(get_player_info_by_room_user_id_list([n.id for n in self._room_user_list]),
                                   key=lambda x: self._user_seat_num_dict[x.room_user_id])
        self._player_id_list = [n.id for n in self._player_list]
        self._first_seat_num = roll_first_action_player(self._room.max_player)
        self._first_index = self._first_seat_num - 1

    async def runtime_process(self):
        await self._broadcast({'message': f'首位玩家座位号: {self._first_seat_num}号'}, self._room_id)
        # loop player action
        max_index = len(self._player_id_list) - 1
        action_index = self._first_index
        end_index = None
        a = 5
        # TODO 如何解决while循环block了await后的方法?
        while True:
            action_player_id = self._player_id_list[action_index]
            set_player_info(action_player_id, {Player.can_action: UserConst.ACTION_CAN})
            # await self._broadcast({"message": f'{action_index + 1}号座位玩家开始行动'}, self._room_id)
            # show player detail
            player_info = get_player_info_by_id(action_player_id)
            # check player online
            if not self.check_user_online(self._room_user_token[player_info.room_user_id]):
                # await self._broadcast({"message": '用户离线...'}, self._room_id)
                pass
            card_detail = json.loads(player_info.card)
            coin_detail = json.loads(player_info.coin)
            source_detail = player_info.source
            # await self._broadcast({"message": f'玩家信息： 卡片：{card_detail}， 硬币： {coin_detail}， 分数： {source_detail}'},
            #                       self._room_id)
            # user action 盖卡，买卡，拿钱
            # room.max_action_time
            wait_player_action(action_player_id, self._room.max_action_time)

            set_player_info(action_player_id, {
                Player.can_action: UserConst.ACTION_NO,
                Player.card: json.dumps(card_detail),
                Player.coin: json.dumps(coin_detail),
                Player.source: source_detail,
            })

            if source_detail >= self._room.win_source:
                end_index = self._first_index - 1 if self._first_index - 1 >= 0 else max_index
                # await self._broadcast({"message": f'玩家达成胜利目标，最后一位可行动玩家为{end_index + 1}号座位'}, self._room_id)

            if end_index == action_index:
                # await self._broadcast({"message": '最后一位玩家行动完毕，游戏结束'}, self._room_id)
                break
            # action finished
            action_index += 1
            if action_index > max_index:
                action_index = 0

            print('------------------')
            await asyncio.sleep(self.action_sleep)
            a -= 1
            if not a:
                break

        # end
        await self._broadcast({"message": '游戏结算'}, self._room_id)
        set_room_info(self._room_id, {RoomSummary.room_status: RoomConst.STATUS_WAITING})
        self.status = RoomConst.STATUS_WAITING

    def check_user_online(self, user_client_token):
        if user_client_token in websocket_router.manager.active_connections[self._room_id]:
            return True
        return False
