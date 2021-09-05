from sqlalchemy import Column, String, Integer, TIMESTAMP, func, text, TEXT, SMALLINT

from utils.mysql_utils import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    mail = Column(String(200), nullable=False)
    password = Column(String(100), nullable=False)
    status = Column(SMALLINT, nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class Player(Base):
    __tablename__ = 'player'

    id = Column(Integer, primary_key=True)
    # ForeignKey('room_user.id')
    room_user_id = Column(Integer)
    # 0 no, 1 yes
    can_action = Column(SMALLINT)
    card = Column(TEXT)
    coin = Column(TEXT)
    source = Column(Integer)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


__all__ = ['User', 'Player']
