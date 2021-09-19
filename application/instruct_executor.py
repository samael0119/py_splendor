import json

from loguru import logger

from service.game_service import CardResource, CoinResource, PlayerResource

# instruct_map = {d: getattr(c, d).__doc__ for c in [CardResource, CoinResource]
#                 for d in dir(c)
#                 if not d.startswith('_') and callable(getattr(c, d))}
from utils.const_utils import CardConst

instruct_map = {
    "buy_card": "买卡片, card_level, card_num",
    "withhold_card": "扣卡片",
    "tack_coin": "拿硬币",
    "pass": "跳过"
}


class InstructExecutor:
    room_resource_map = {}

    def init_room_resource(self, room_id: int, card_resource: CardResource,
                           coin_resource: CoinResource, player_resource: PlayerResource):
        self.room_resource_map[room_id] = {
            "card": card_resource,
            "coin": coin_resource,
            "player": player_resource
        }

    def execute(self, room_id: int, instruct: dict):
        if "instruct" not in instruct:
            return
        if instruct['instruct'] == 'buy_card':
            # 只能买明牌或手里扣留的牌
            if instruct.get('card_type') not in {CardConst.TYPE_OPEN_CARD, CardConst.TYPE_WITHHOLDING_CARD}:
                return
            self.check_player_can_buy_card(room_id, instruct.get('card_type'), instruct.get('card_num'))
        elif instruct['instruct'] == 'withhold_card':
            pass
        else:
            logger.info(f"无效指令: {instruct['instruct']}")

    def check_player_can_buy_card(self, room_id, card_type, card_num):
        card = self.room_resource_map[room_id]['card'].get_card_info()

    def check_player_can_take_coin(self, player, coin):
        pass


instruct_executor = InstructExecutor()
