from random import choice


def get_room_list():
    """
    need page util
    :return:
    """
    pass


def get_room_info(room_id):
    pass


def start_game(room_id):
    pass


def game_init(card_summary_id, coin_summary_id):
    """
    初始化游戏，币池，卡池
    :param card_summary_id:
    :param coin_summary_id:
    :return:
    """
    pass


def roll_first_action_player(user_count: int):
    """
    获取首位玩家id
    :param user_count:
    :return:
    """
    return choice(range(1, user_count + 1))

