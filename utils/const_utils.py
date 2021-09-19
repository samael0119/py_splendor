class ServiceCode:
    SUCCESS = 1000
    SQL_ERROR = 2000
    SYS_ERROR = 3000
    Permission_Error = 4000


class ResponseCode:
    SUCCESS = 200
    UNKNOWN = 400
    FAILED = 500


class RoomStatusCode:
    WAITING = 1
    GAMING = 2
    CLOSED = 3


class UserStatusCode:
    DISABLED = -1
    FREE = 1
    IN_ROOM = 2
    READY = 3
    GAMING = 4
    OBSERVING = 5


class UserConst:
    STATUS_FREE = 1
    STATUS_IN_ROOM = 2
    STATUS_GAMING = 3
    STATUS_OBSERVING = 4
    STATUS_DISABLED = -1

    ACTION_CAN = 1
    ACTION_NO = 0

    ACTION_PASS = ''
    ACTION_TACK_COIN = ''
    ACTION_BUY_CARD = ''
    ACTION_SEIZURE_CARD = ''


class RoomConst:
    ROOM_MAX_COUNT = 1

    PLAYER_MAX_COUNT = 4
    PLAYER_MIN_COUNT = 2
    PLAYER_MAX_ACTION_TIME = 300
    PLAYER_MIN_ACTION_TIME = 5

    OBSERVER_MAX_COUNT = 6
    OBSERVER_MIN_COUNT = 0

    STATUS_WAITING = 1
    STATUS_GAMING = 2
    STATUS_CLOSED = 3

    TYPE_PLAYER = 11
    TYPE_OBSERVER = 12


class CardConst:
    LEVEL_1_CARD = '一级卡'
    LEVEL_2_CARD = '二级卡'
    LEVEL_3_CARD = '三级卡'
    NOBLE_CARD = '贵族卡'

    TYPE_OPEN_CARD = '明牌'
    TYPE_DARK_CARD = '暗牌'
    TYPE_WITHHOLDING_CARD = '玩家扣留的卡'


class CoinConst:
    COLOR_BLACK = '黑色'
    COLOR_WHITE = '白色'
    COLOR_RED = '红色'
    COLOR_BLUE = '蓝色'
    COLOR_GREEN = '绿色'
    COLOR_GOLD = '金色'

    OBJECT = 'object'
    COUNT = 'count'

    ROLE_PLAYER_COIN_MAP = {
        2: 4,
        3: 5,
        4: 7
    }


class SystemConst:
    ACTION_START = "start"
    ACTION_READY = "ready"
