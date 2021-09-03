import time

from loguru import logger
from timeout_decorator import timeout

from model.user import Player
from service.game_service import game_init, roll_first_action_player, get_room_info, set_room_info
from service.user_service import get_player_info, get_player_card, get_player_coin, get_player_source, set_player_info, \
    wait_player_action
from utils.redis_utils import RedisConnector
from model.game import RoomSummary
from utils.const_utils import ServiceCode
import json


def play(room_id):
    # get_room_info
    room = get_room_info(room_id)

    # set_room_status
    res = set_room_info(room_id, {RoomSummary.room_status: ''})
    if res != ServiceCode.SUCCESS:
        logger.error('房间状态改变失败')
        return

    # new thread

    # init game
    card_data, coin_data = game_init(room.card_summary_id, room.coin_summary_id)

    # add to redis
    # redis_conn = RedisConnector().get_conn()

    # roll first player
    player_list = sorted([get_player_info(n) for n in json.loads(room.player_list)], key=lambda x: x.seat_num)
    first_index = roll_first_action_player(room.max_player)
    logger.info(f'首位玩家座位号: {first_index + 1}号')

    # loop player action
    max_index = len(player_list) - 1
    action_index = first_index
    end_index = None
    while True:
        action_player = player_list[action_index]
        set_player_info(action_player.id, {Player.is_action: 1})
        logger.info(f'{action_index+1}号座位玩家开始行动')
        # show player detail
        card_detail = get_player_card(action_player.id)
        coin_detail = get_player_coin(action_player.id)
        source_detail = get_player_source(action_player.id)
        logger.info(f'玩家信息： 卡片：{card_detail["dict"]}， 硬币： {coin_detail["dict"]}， 分数： {source_detail["dict"]}')
        # user action 盖卡，买卡，拿钱
        # room.max_action_time
        wait_player_action(room_id, action_player.id, room.max_action_time)

        if action_player.source >= room.win_source:
            end_index = first_index - 1 if first_index - 1 >= 0 else max_index
            logger.info(f'有玩家达成胜利目标，最后一位可行动玩家为{end_index + 1}号座位')

        if end_index == action_index:
            logger.info('最后一位玩家行动完毕，游戏结束，开始结算')
            break
        # action finished
        action_index += 1
        if action_index == max_index:
            action_index = 0

    # end

    pass


if __name__ == '__main__':
    play(1)
