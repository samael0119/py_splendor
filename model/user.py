from sqlalchemy import Column, String, Integer, TEXT, SMALLINT

from utils.mysql_utils import BaseModel, Base


class User(BaseModel, Base):
    __tablename__ = 'user'

    name = Column(String(100), nullable=False)
    icon_id = Column(Integer)
    mail = Column(String(200), nullable=False)
    password = Column(String(100), nullable=False)
    status = Column(SMALLINT, nullable=False)


__all__ = ['User']
