from sqlalchemy import Column, String, Integer, TEXT, SMALLINT

from utils.mysql_utils import BaseModel, Base


class User(BaseModel, Base):
    __tablename__ = 'user'

    name = Column(String(100), nullable=False)
    icon_id = Column(Integer)
    mail = Column(String(200), nullable=False)
    password = Column(String(100), nullable=False)
    status = Column(SMALLINT, nullable=False)


class Player(BaseModel, Base):
    __tablename__ = 'player'

    # ForeignKey('room_user.id')
    room_user_id = Column(Integer)
    # 0 no, 1 yes
    can_action = Column(SMALLINT)
    card = Column(TEXT)
    coin = Column(TEXT)
    source = Column(Integer)


__all__ = ['User', 'Player']
