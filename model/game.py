from sqlalchemy import Column, String, Integer, TIMESTAMP, func, text, SMALLINT

from utils.mysql_utils import Base


class RoomSummary(Base):
    __tablename__ = 'room_summary'

    id = Column(Integer, primary_key=True)
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
    room_status = Column(String(20))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class RoomUser(Base):
    __tablename__ = 'room_user'

    id = Column(Integer, primary_key=True)
    # ForeignKey('room_summary.id')
    room_id = Column(Integer)
    # ForeignKey('user.id')
    user_id = Column(Integer)
    # player, observer
    user_type = Column(String(20))
    seat_num = Column(Integer)
    # null, ready, gaming, observing
    user_status = Column(String(20))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


__all__ = ['RoomSummary', 'RoomUser']
