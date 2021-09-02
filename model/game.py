from sqlalchemy import Column, String, Integer, TIMESTAMP, func, text, ForeignKey, SMALLINT

from utils.mysql_utils import Base


class RoomSummary(Base):
    __tablename__ = 'room_summary'

    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('user.id'))
    password = Column(String(100))
    first_player = Column(SMALLINT)
    player_list = Column(String(200))
    card_summary_id = Column(Integer, ForeignKey('card_summary.id'))
    coin_summary_id = Column(Integer, ForeignKey('coin_summary.id'))
    # Waiting, Gaming, Closed
    room_status = Column(String(20))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class RoomUser(Base):
    __tablename__ = 'room_user'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('room_summary.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    # player, observer
    user_type = Column(String(20))
    # null, ready, gaming, watching
    user_status = Column(String(20))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


__all__ = ['RoomSummary', 'RoomUser']
