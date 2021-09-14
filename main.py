from loguru import logger

from model import card, coin, game, icon, user
from utils.mysql_utils import Base


def db_init():
    try:
        Base.metadata.create_all()
    except:
        logger.exception('database init failed')
    logger.success("create tables success")


def main():
    db_init()


if __name__ == '__main__':
    main()
