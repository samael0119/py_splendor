from loguru import logger

from sqlalchemy import and_, or_

from model.card import CardSummary, CardDetail, CardRelate
from utils.const_utils import ServiceCode
from utils.mysql_utils import MysqlConnector
from utils.page_utils import PageHelper


def create_card_summary(name, describe):
    new_card_summary = CardSummary(name=name, describe=describe)
    with MysqlConnector().get_session() as s:
        try:
            s.add(new_card_summary)
            s.commit()
        except:
            logger.exception('添加卡包失败')
            s.rollback()
            return ServiceCode.SQL_ERROR
    logger.info('添加卡包成功')
    return ServiceCode.SUCCESS


def delete_card_summary(card_summary_id):
    with MysqlConnector().get_session() as s:
        try:
            s.query(CardSummary).filter(CardSummary.id == card_summary_id).delete(synchronize_session='fetch')
            s.commit()
        except:
            logger.exception('删除卡包失败')
            s.rollback()
            return ServiceCode.SQL_ERROR
    logger.info('删除卡包成功')
    return ServiceCode.SUCCESS


def update_card_summary(card_summary_id, name, describe):
    with MysqlConnector().get_session() as s:
        try:
            s.query(CardSummary).filter(CardSummary.id == card_summary_id).update({
                'name': name,
                'describe': describe
            }, synchronize_session='fetch')
            s.commit()
        except:
            logger.exception('修改卡包失败')
            s.rollback()
            return ServiceCode.SQL_ERROR
    logger.info('修改卡包成功')
    return ServiceCode.SUCCESS


def list_card_summary(card_summary_id=None, name=None, describe=None, page_no=1, page_size=10):
    total_page = 1
    page_data = []
    with MysqlConnector().get_session() as s:
        try:
            if all([not n for n in [card_summary_id, name, describe]]):
                ph = PageHelper(s.query(CardSummary), page_size)
                total_page = ph.get_total_page()
                page_data.extend(ph.get_page(page_no))
            else:
                q = s.query(CardSummary)
                if card_summary_id:
                    page_data.extend(q.filter(CardSummary.id == card_summary_id).all())
                else:
                    condition = []
                    if name:
                        condition.append(CardSummary.name.like(f'%{name}%'))
                    if describe:
                        condition.append(CardSummary.describe.like(f'%{describe}%'))

                    if condition:
                        q_condition = q.filter(or_(*condition))
                        ph = PageHelper(q_condition, page_size)
                        total_page = ph.get_total_page()
                        page_data.extend(ph.get_page(page_no))
        except:
            logger.exception('获取卡包失败')

    logger.info(f'获取卡包第{page_no}页，page_size: {page_size}')
    return total_page, page_data


def get_card_detail_list_by_summary_id(card_summary_id):
    card_detail_list = []
    with MysqlConnector().get_session() as s:
        try:
            card_detail_list.extend(s.query(CardDetail).filter(CardDetail.id.in_(
                s.query(CardRelate.card_detail_id).filter(CardRelate.card_summary_id == card_summary_id)
            )).all())
        except:
            logger.exception(f'获取卡包{card_summary_id}信息失败')
            return card_detail_list

    logger.info(f'获取卡包{card_summary_id}信息成功')
    return card_detail_list

