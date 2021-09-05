import json
import time

from loguru import logger

from model.game import RoomSummary
from model.user import Player
from service.game_service import game_init, roll_first_action_player, get_room_info, set_room_info, get_room_player_list
from service.user_service import set_player_info, wait_player_action, get_player_info_by_room_user_id_list, \
    get_player_info_by_id
from utils.const_utils import ServiceCode, RoomConst, UserConst


def play(room_id):
    # get_room_info
    room = get_room_info(room_id)

    # set_room_status
    res = set_room_info(room_id, {RoomSummary.room_status: RoomConst.STATUS_GAMING})
    if res != ServiceCode.SUCCESS:
        logger.error('房间状态改变失败')
        return

    # new thread

    # init game
    card_data, coin_data = game_init(room.card_summary_id, room.coin_summary_id)

    # add to redis
    # redis_conn = RedisConnector().get_conn()

    # roll first player
    room_user_list = get_room_player_list(room_id)
    user_seat_num_dict = {n.id: n.seat_num for n in room_user_list}
    player_list = sorted(get_player_info_by_room_user_id_list([n.id for n in room_user_list]),
                         key=lambda x: user_seat_num_dict[x.room_user_id])
    player_id_list = [n.id for n in player_list]
    first_seat_num = roll_first_action_player(room.max_player)
    first_index = first_seat_num - 1
    logger.info(f'首位玩家座位号: {first_seat_num}号')

    # loop player action
    max_index = len(player_id_list) - 1
    action_index = first_index
    end_index = None
    while True:
        action_player_id = player_id_list[action_index]
        set_player_info(action_player_id, {Player.can_action: UserConst.ACTION_CAN})
        logger.info(f'{action_index + 1}号座位玩家开始行动')
        # show player detail
        player_info = get_player_info_by_id(action_player_id)
        card_detail = json.loads(player_info.card)
        coin_detail = json.loads(player_info.coin)
        source_detail = player_info.source
        logger.info(f'玩家信息： 卡片：{card_detail}， 硬币： {coin_detail}， 分数： {source_detail}')
        # user action 盖卡，买卡，拿钱
        # room.max_action_time
        wait_player_action(action_player_id, room.max_action_time)

        set_player_info(action_player_id, {Player.can_action: UserConst.ACTION_NO})

        if source_detail >= room.win_source:
            end_index = first_index - 1 if first_index - 1 >= 0 else max_index
            logger.info(f'有玩家达成胜利目标，最后一位可行动玩家为{end_index + 1}号座位')

        if end_index == action_index:
            logger.info('最后一位玩家行动完毕，游戏结束，开始结算')
            break
        # action finished
        action_index += 1
        if action_index > max_index:
            action_index = 0

        time.sleep(1)

    # end

    pass


if __name__ == '__main__':
    play(4)
