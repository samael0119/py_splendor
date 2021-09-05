from sqlalchemy import Column, String, Integer, TIMESTAMP, func, text

from utils.mysql_utils import Base


class CardSummary(Base):
    __tablename__ = 'card_summary'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    describe = Column(String(100))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class CardDetail(Base):
    __tablename__ = 'card_detail'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    # ForeignKey('card_type.id')
    card_type_id = Column(Integer)
    price = Column(String(100), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class CardType(Base):
    __tablename__ = 'card_type'

    id = Column(Integer, primary_key=True)
    card_type = Column(String(100))
    describe = Column(String(100))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class CardRelate(Base):
    __tablename__ = 'card_relate'

    id = Column(Integer, primary_key=True)
    # ForeignKey('card_summary.id')
    card_summary_id = Column(Integer)
    # ForeignKey('card_detail.id')
    card_detail_id = Column(Integer)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


__all__ = ['CardSummary', 'CardDetail', 'CardType', 'CardRelate']
