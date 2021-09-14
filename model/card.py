from sqlalchemy import Column, String, Integer

from utils.mysql_utils import BaseModel, Base


class CardSummary(BaseModel, Base):
    __tablename__ = 'card_summary'

    name = Column(String(100))
    describe = Column(String(100))


class CardDetail(BaseModel, Base):
    __tablename__ = 'card_detail'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    card_icon_id = Column(Integer)
    card_type = Column(String(100), nullable=False)
    card_source = Column(Integer, nullable=False)
    card_color = Column(String(20), nullable=False)
    card_price = Column(String(100), nullable=False)


class CardRelate(BaseModel, Base):
    __tablename__ = 'card_relate'

    # ForeignKey('card_summary.id')
    card_summary_id = Column(Integer)
    # ForeignKey('card_detail.id')
    card_detail_id = Column(Integer)


__all__ = ['CardSummary', 'CardDetail', 'CardRelate']
