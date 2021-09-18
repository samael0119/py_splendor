from collections import deque
from random import randint, shuffle

from loguru import logger

from model.card import CardDetail
from model.coin import CoinDetail
from model.game import RoomSummary, RoomUser
from service.card_service import get_card_detail_list_by_summary_id
from service.coin_service import get_coin_detail_list_by_summary_id
from utils.const_utils import ServiceCode, RoomConst, CardConst, CoinConst
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
    logger.debug(f'修改房间{room_id}信息成功')
    return ServiceCode.SUCCESS


def start_game(room_id):
    pass


class CardResource(CardDetail):
    """
    牌堆， index=0代表牌堆顶， -1代表牌堆底
    """
    card_resource = {
        CardConst.LEVEL_1_CARD: {
            CardConst.TYPE_DARK_CARD: deque(),
            CardConst.TYPE_OPEN_CARD: deque(maxlen=4),
        },
        CardConst.LEVEL_2_CARD: {
            CardConst.TYPE_DARK_CARD: deque(),
            CardConst.TYPE_OPEN_CARD: deque(maxlen=4),
        },
        CardConst.LEVEL_3_CARD: {
            CardConst.TYPE_DARK_CARD: deque(),
            CardConst.TYPE_OPEN_CARD: deque(maxlen=4),
        },
        CardConst.NOBLE_CARD: {
            CardConst.TYPE_DARK_CARD: deque(),
            CardConst.TYPE_OPEN_CARD: deque(maxlen=4),
        },
    }

    def __init__(self, shuffled_card_list):
        for c in shuffled_card_list:
            self.card_resource[c.card_type][CardConst.TYPE_DARK_CARD].append(c)

        for k, v in self.card_resource.items():
            for _ in range(v[CardConst.TYPE_OPEN_CARD].maxlen):
                logger.debug(f"发牌: {k}, 牌堆: {CardConst.TYPE_DARK_CARD}")
                v[CardConst.TYPE_OPEN_CARD].extend(self.deal_card(k, CardConst.TYPE_DARK_CARD, 1))

    def take_card(self, card_level, card_type, index):
        """拿牌，需要支付卡片相应费用"""
        card = None
        if card_type == CardConst.TYPE_DARK_CARD:
            card_list = self.deal_card(card_level, card_type, 1)
            if card_list:
                card = card_list[0]
        else:
            if self.card_resource[card_level][card_type][index]:
                card = self.card_resource[card_level][card_type][index]
                card_list = self.deal_card(card_level, card_type, 1)
                if card_list:
                    self.card_resource[card_level][card_type][index] = card_list[0]

        if card:
            logger.debug(f'拿卡成功，card: {card}')
        else:
            logger.debug('拿卡失败')
        return card

    def deal_card(self, card_level, card_type, count):
        """发牌，从卡池顶发指定张数的牌，系统方法玩家无法使用"""
        card_list = []
        for _ in range(count):
            if len(self.card_resource[card_level][card_type]) >= 1:
                card = self.card_resource[card_level][card_type].popleft()
                if card_type == CardConst.TYPE_OPEN_CARD:
                    logger.debug(f'发牌, card: {card}')
                elif card_type == CardConst.TYPE_DARK_CARD:
                    logger.debug(f'扣牌{count}张')
                card_list.append(card)
                logger.debug(f'[{card_level}][{card_type}]剩余{len(self.card_resource[card_level][card_type])}张')
            else:
                logger.debug(f'[{card_level}][{card_type}]没有牌了')
                break
        return card_list


class CoinResource(CoinDetail):
    coin_resource = {
        CoinConst.COLOR_GREEN: {
            CoinConst.OBJECT: None,
            CoinConst.COUNT: 0
        },
        CoinConst.COLOR_RED: {
            CoinConst.OBJECT: None,
            CoinConst.COUNT: 0
        },
        CoinConst.COLOR_BLUE: {
            CoinConst.OBJECT: None,
            CoinConst.COUNT: 0
        },
        CoinConst.COLOR_BLACK: {
            CoinConst.OBJECT: None,
            CoinConst.COUNT: 0
        },
        CoinConst.COLOR_WHITE: {
            CoinConst.OBJECT: None,
            CoinConst.COUNT: 0
        },
        CoinConst.COLOR_GOLD: {
            CoinConst.OBJECT: None,
            CoinConst.COUNT: 0
        }
    }

    def __init__(self, shuffled_coin_list, player_count):
        for c in shuffled_coin_list:
            count = CoinConst.ROLE_PLAYER_COIN_MAP[player_count]
            # gold coin num?
            # if c.coin_color == CoinConst.COLOR_GOLD:
            #     count =
            self.coin_resource[c.coin_color].update({
                CoinConst.OBJECT: c,
                CoinConst.COUNT: count
            })

    def tack_coin(self, coin_colors):
        """获取硬币"""
        coin_list = []
        for color in coin_colors:
            if self.coin_resource[color][CoinConst.COUNT] >= 0:
                coin_list.append(self.coin_resource[color][CoinConst.OBJECT])
                self.coin_resource[color][CoinConst.COUNT] -= 1
                logger.debug(f'{color}拿取成功，剩余{self.coin_resource[color][CoinConst.COUNT]}枚')
            else:
                logger.debug(f'{color}硬币数量不足，拿币失败')
        return coin_list


def game_resource_init(card_summary_id, coin_summary_id, player_count):
    """
    初始化游戏资源，币池，卡池
    :param card_summary_id:
    :param coin_summary_id:
    :param player_count:
    :return:
    """
    card_detail_list = (get_card_detail_list_by_summary_id(card_summary_id=card_summary_id))
    coin_detail_list = get_coin_detail_list_by_summary_id(coin_summary_id=coin_summary_id)

    if any([not n for n in [card_summary_id, coin_summary_id]]):
        return card_detail_list, coin_detail_list

    shuffle(card_detail_list)
    shuffle(coin_detail_list)

    card_resource = CardResource(card_detail_list)
    coin_resource = CoinResource(coin_detail_list, player_count)
    return card_resource, coin_resource


def roll_first_action_player(user_count: int):
    """
    获取首位玩家seat_num
    :param user_count:
    :return:
    """
    return randint(1, user_count)
