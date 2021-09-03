class ServiceCode:
    SUCCESS = 1000
    SQL_ERROR = 2000
    SYS_ERROR = 3000


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
