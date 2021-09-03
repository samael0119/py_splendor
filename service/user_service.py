import threading
import time

from loguru import logger

from model.user import Player


def logon():
    pass


def login():
    pass


def logout():
    pass


def get_player_info(player_id):
    return Player()


def set_player_info(player_id, values):
    pass


def create_room(user_id):
    pass


def join_room(user_id, room_id):
    pass


def set_room_info(room_id, room):
    pass


def join_player_position():
    pass


def join_observer_position():
    pass


def leave_room():
    pass


def begin_player_action():
    pass


def finish_player_action():
    pass


def get_player_card(player_id):
    pass


def get_player_coin(player_id):
    pass


def get_player_source(player_id):
    pass


def finish_log():
    logger.info('行动超时，终止行动')


def wait_player_action(room_id, player_id, time_out):
    # 线程计时器
    t = threading.Timer(time_out, finish_log)
    t.start()
    while True:
        # 玩家执行跳过 或 行动超时
        if not get_player_info(player_id).is_action or not t.is_alive():
            break
        time.sleep(1)


def finish_action(player_id):
    pass
