from sqlalchemy import Column, String, Integer, TIMESTAMP, func, text, Text

from utils.mysql_utils import Base


class IconDetail(Base):
    __tablename__ = 'icon_detail'

    id = Column(Integer, primary_key=True)
    describe = Column(String(100))
    base64_code = Column(Text)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))