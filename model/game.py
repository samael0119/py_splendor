from sqlalchemy import Column, String, Integer, SMALLINT

from utils.mysql_utils import BaseModel, Base


class RoomSummary(BaseModel, Base):
    __tablename__ = 'room_summary'

    # ForeignKey('user.id')
    owner = Column(Integer)
    password = Column(String(100))
    first_player = Column(SMALLINT)
    max_player = Column(Integer)
    max_action_time = Column(Integer)
    win_source = Column(Integer)
    # ForeignKey('card_summary.id')
    card_summary_id = Column(Integer)
    # ForeignKey('coin_summary.id')
    coin_summary_id = Column(Integer)
    # Waiting, Gaming, Closed
    room_status = Column(SMALLINT)


class RoomUser(BaseModel, Base):
    __tablename__ = 'room_user'

    # ForeignKey('room_summary.id')
    room_id = Column(Integer)
    # ForeignKey('user.id')
    user_id = Column(Integer)
    # player, observer
    user_type = Column(String(20))
    seat_num = Column(Integer)
    # null, ready, gaming, observing
    user_status = Column(String(20))
    user_client_token = Column(String(32))


__all__ = ['RoomSummary', 'RoomUser']
