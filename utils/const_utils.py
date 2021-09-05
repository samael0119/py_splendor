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


class RoomConst:
    GLOBAL_MAX_ROOM_COUNT = 1

    PLAYER_MAX_COUNT = 6
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

