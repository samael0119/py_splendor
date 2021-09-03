import os

import redis


class RedisConnector:

    def __init__(self):
        self._host = os.getenv('REDIS_HOST', '127.0.0.1')
        self._port = os.getenv('REDIS_PORT', '6379')
        self._db = os.getenv('REDIS_DB', '0')
        self._auth = os.getenv('REDIS_AUTH', '123qwe')
        self._pool = redis.ConnectionPool(host=self._host, port=int(self._port), db=int(self._db), password=self._auth)

    def get_conn(self):
        return redis.Redis(connection_pool=self._pool)
