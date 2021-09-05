from random import randint

from loguru import logger

from model.game import RoomSummary, RoomUser
from utils.const_utils import ServiceCode, RoomConst, UserConst
from utils.mysql_utils import MysqlConnector


def get_room_list():
    """
    need page util
    :return:
    """
    pass


def get_room_info(room_id):
    with MysqlConnector().get_session() as s:
        try:
            item = s.query(RoomSummary).filter(RoomSummary.id == room_id).first()
        except:
            logger.exception(f'查询房间{room_id}信息失败')
            return None

    return item


def get_room_user_list(room_id):
    with MysqlConnector().get_session() as s:
        try:
            user_list = s.query(RoomUser).filter(RoomUser.room_id == room_id).all()
        except:
            logger.exception(f'查询房间{room_id}用戶信息失败')
            return []

    return user_list


def get_room_player_list(room_id):
    with MysqlConnector().get_session() as s:
        try:
            player_list = s.query(RoomUser).filter(RoomUser.room_id == room_id,
                                                   RoomUser.user_type == RoomConst.TYPE_PLAYER).all()
        except:
            logger.exception(f'查询房间{room_id}用戶信息失败')
            return []

    return player_list


def get_room_observer_list(room_id):
    with MysqlConnector().get_session() as s:
        try:
            observer_list = s.query(RoomUser).filter(RoomUser.room_id == room_id,
                                                     RoomUser.user_type == RoomConst.TYPE_OBSERVER).all()
        except:
            logger.exception(f'查询房间{room_id}用戶信息失败')
            return []

    return observer_list


def set_room_info(room_id, values):
    with MysqlConnector().get_session() as s:
        try:
            s.query(RoomSummary).filter(RoomSummary.id == room_id).update(values, synchronize_session='fetch')
            s.commit()
        except:
            logger.exception(f'修改房间{room_id}信息失败')
            s.rollback()
            return ServiceCode.SQL_ERROR
    logger.info(f'修改房间{room_id}信息成功')
    return ServiceCode.SUCCESS


def start_game(room_id):
    pass


def game_init(card_summary_id, coin_summary_id):
    """
    初始化游戏，币池，卡池
    :param card_summary_id:
    :param coin_summary_id:
    :return:
    """
    return [], []


def roll_first_action_player(user_count: int):
    """
    获取首位玩家seat_num
    :param user_count:
    :return:
    """
    return randint(1, user_count)
