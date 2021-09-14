from sqlalchemy import Column, String, Integer

from utils.mysql_utils import BaseModel, Base


class CoinSummary(BaseModel, Base):
    __tablename__ = 'coin_summary'

    name = Column(String(100))


class CoinDetail(BaseModel, Base):
    __tablename__ = 'coin_detail'

    coin_color = Column(String(100))
    coin_icon_id = Column(Integer)


class CoinRelate(BaseModel, Base):
    __tablename__ = 'coin_relate'

    # ForeignKey('coin_summary.id')
    coin_summary_id = Column(Integer)
    # ForeignKey('coin_detail.id')
    coin_detail_id = Column(Integer)


__all__ = ['CoinSummary', 'CoinDetail', 'CoinRelate']
