import json
import threading
import time
from uuid import uuid1

from loguru import logger

from model.game import RoomSummary, RoomUser
from model.user import User
from service.game_service import get_room_info
from utils.const_utils import ServiceCode, RoomConst, UserConst
from utils.mysql_utils import MysqlConnector


def logon():
    pass


def login():
    pass


def logout():
    pass


def create_room(user_id, max_player=4, max_action_time=30, win_source=10, card_summary_id=1, coin_summary_id=1):
    new_room = RoomSummary(owner=user_id,
                           max_player=max_player,
                           max_action_time=max_action_time,
                           win_source=win_source,
                           card_summary_id=card_summary_id,
                           coin_summary_id=coin_summary_id,
                           room_status=RoomConst.STATUS_WAITING)
    with MysqlConnector().get_session() as s:
        try:
            s.add(new_room)
            s.commit()
        except:
            logger.exception(f'{user_id}创建房间失败')
            s.rollback()
            return ServiceCode.SQL_ERROR
        logger.info(f'{user_id}创建房间{new_room.id}成功')

        # 创建者无法加入自己的房间则删除该房间
        if ServiceCode.SUCCESS != join_room(user_id=user_id, room_id=new_room.id):
            s.query(RoomSummary).filter(RoomSummary.id == new_room.id).delete(synchronize_session='fetch')
            s.commit()
            return ServiceCode.SYS_ERROR

    return ServiceCode.SUCCESS


def check_room_can_join(room_id, user_type=RoomConst.TYPE_PLAYER):
    with MysqlConnector().get_session() as s:
        try:
            item = s.query(RoomSummary).filter(RoomSummary.id == room_id).first()
        except:
            logger.exception(f'查询房间{room_id}信息失败')
            return False
        if item and item.room_status == RoomConst.STATUS_WAITING:
            item_list = s.query(RoomUser).filter(RoomUser.room_id == room_id,
                                                 RoomUser.user_type == user_type).all()
            if user_type == RoomConst.TYPE_PLAYER and len(item_list) < item.max_player:
                return True
            elif user_type == RoomConst.TYPE_OBSERVER and len(item_list) < RoomConst.OBSERVER_MAX_COUNT:
                return True
    return False


def check_user_can_join(user_id):
    with MysqlConnector().get_session() as s:
        try:
            item = s.query(User).filter(User.id == user_id).first()
        except:
            logger.exception(f'查询用户{user_id}信息失败')
            return False
    if item and item.status == UserConst.STATUS_FREE:
        return True
    return False


def check_room_token_can_join(room_id, client_id):
    with MysqlConnector().get_session() as s:
        try:
            items = s.query(RoomUser).filter(RoomUser.room_id == room_id).all()
        except:
            logger.exception(f'查询房间{room_id}信息失败')
            return None
        if not room_id:
            logger.error(f'房间{room_id}不存在')
            return None
        if client_id:
            for item in items:
                if client_id == item.user_client_token:
                    user = s.query(User).filter(User.id == item.user_id).first()
                    room = s.query(RoomSummary).filter(RoomSummary.id == item.room_id).first()
                    if any([not n for n in [user, room]]):
                        return None
                    if room.room_status == RoomConst.STATUS_CLOSED:
                        return None

                    result = {}
                    result.update({
                        "user_id": user.id,
                        "user_name": user.name,
                        "room_user_id": item.id,
                        "user_type": item.user_type,
                        "room_owner": room.owner == user.id,
                    })
                    return result
    return None


def get_room_seat_num(room_id):
    result = []
    item = get_room_info(room_id)
    if not item:
        return result
    with MysqlConnector().get_session() as s:
        max_seat_num = item.max_player
        exist_seat_num = [n for n in s.query(RoomUser.seat_num).filter(RoomUser.room_id == room_id).all() if n[0]]
        result.extend(set(range(1, max_seat_num + 1)).difference(set(exist_seat_num)))

    return sorted(result)


def join_room(user_id, room_id, user_type=RoomConst.TYPE_PLAYER):
    if not check_user_can_join(user_id=user_id):
        return ServiceCode.SYS_ERROR

    if not check_room_can_join(room_id=room_id, user_type=user_type):
        return ServiceCode.SYS_ERROR

    # 获取可坐下的座位号，默认坐在最小的号码
    seat_num_list = get_room_seat_num(room_id=room_id)

    new_room_user = RoomUser(user_id=user_id,
                             room_id=room_id,
                             user_type=user_type,
                             seat_num=seat_num_list[0],
                             user_client_token=uuid1().hex
                             )
    with MysqlConnector().get_session() as s:
        try:
            s.add(new_room_user)
            s.commit()
        except:
            logger.exception(f'{user_id}加入房间{room_id}失败')
            s.rollback()
            return ServiceCode.SQL_ERROR
    logger.info(f'{user_id}加入房间{room_id}成功')
    return ServiceCode.SUCCESS


def player_sit_down(room_id, room_user_id, seat_num=None):
    seat_num_list = get_room_seat_num(room_id)
    with MysqlConnector().get_session() as s:
        try:
            new_seat_num = seat_num or seat_num_list[0]
            s.query(RoomUser).filter(RoomUser.id == room_user_id).update({
                'seat_num': new_seat_num
            }, synchronize_session='fetch')
            s.commit()
        except:
            logger.exception(f'{room_user_id}入座{room_id}的{new_seat_num}号座位失败')
            s.rollback()
            return ServiceCode.SQL_ERROR

    logger.info(f'{room_user_id}入座{room_id}的{new_seat_num}号座位成功')
    return ServiceCode.SUCCESS


def set_room_info(room_id, values):
    pass


def leave_room():
    pass


def begin_player_action():
    pass


def finish_player_action():
    pass


def finish_log():
    logger.info('行动超时，终止行动')


def wait_player_action(player_resource, player_id, time_out):
    # 线程计时器
    t = threading.Timer(time_out, finish_log)
    t.start()
    while True:
        # 玩家执行跳过 或 行动超时
        if player_resource.resource[player_id]['can_action'] != UserConst.ACTION_CAN or not t.is_alive():
            break
        time.sleep(1)


def finish_action(player_id):
    pass


if __name__ == '__main__':
    # create_room(1)
    join_room(3, 5)
    # player_sit_down(4, 3, 2)
