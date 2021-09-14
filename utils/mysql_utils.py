import os

from sqlalchemy import create_engine, MetaData, Column, TIMESTAMP, func, text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils.functions import database_exists, create_database


class MysqlConnector:
    _conn_url = os.getenv('MYSQL_CONN_URL', 'mysql+pymysql://root:123qwe@localhost:33060')
    _database = os.getenv('MYSQL_DATABASE', 'py_splendor')
    _engine = None
    _db_session = None

    def __init__(self):
        if not self._engine:
            self._engine = create_engine(f"{self._conn_url}/{self._database}",
                                         pool_size=20, pool_recycle=3600)
            if not database_exists(self._engine.url):
                create_database(self._engine.url, encoding='utf8mb4')

    def get_session(self):
        if self._db_session is not None:
            return self._db_session()

        else:
            self._db_session = sessionmaker(bind=self._engine)
            return self._db_session()

    def get_base(self):
        return declarative_base(bind=self._engine)

    def get_metadata(self):
        return MetaData(bind=self._engine)

    def get_engine(self):
        return self._engine


Base = MysqlConnector().get_base()
metadata = MysqlConnector().get_metadata()


class BaseModel:

    id = Column(Integer, primary_key=True)
    create_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    update_time = Column(TIMESTAMP, nullable=False,
                         server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
