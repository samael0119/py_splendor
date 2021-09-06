from loguru import logger

from model.coin import CoinDetail, CoinRelate
from utils.mysql_utils import MysqlConnector


def create_coin_summary():
    pass


def delete_coin_summary():
    pass


def update_coin_summary():
    pass


def list_coin_summary():
    pass


def get_coin_detail_list_by_summary_id(coin_summary_id):
    coin_detail_list = []
    with MysqlConnector().get_session() as s:
        try:
            coin_detail_list.extend(s.query(CoinDetail).filter(CoinDetail.id.in_(
                s.query(CoinRelate.coin_detail_id).filter(CoinRelate.coin_summary_id == coin_summary_id)
            )).all())
        except:
            logger.exception(f'获取币包{coin_summary_id}信息失败')
            return coin_detail_list

    logger.info(f'获取币包{coin_summary_id}信息成功')
    return coin_detail_list
