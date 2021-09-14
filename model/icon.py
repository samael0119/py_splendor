from sqlalchemy import Column, String, Text

from utils.mysql_utils import BaseModel, Base


class IconDetail(BaseModel, Base):
    __tablename__ = 'icon_detail'

    describe = Column(String(100))
    base64_code = Column(Text)
