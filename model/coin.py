from sqlalchemy import Column, String, Integer, TIMESTAMP, func, text

from utils.mysql_utils import Base


class CoinSummary(Base):
    __tablename__ = 'coin_summary'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class CoinDetail(Base):
    __tablename__ = 'coin_detail'

    id = Column(Integer, primary_key=True)
    color = Column(String(100))
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class CoinRelate(Base):
    __tablename__ = 'coin_relate'

    id = Column(Integer, primary_key=True)
    # ForeignKey('coin_summary.id')
    coin_summary_id = Column(Integer)
    # ForeignKey('coin_detail.id')
    coin_detail_id = Column(Integer)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


__all__ = ['CoinSummary', 'CoinDetail', 'CoinRelate']
