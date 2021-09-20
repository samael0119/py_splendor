from service.game_service import CardResource, CoinResource, PlayerResource
from utils.const_utils import CardConst, CoinConst, UserConst


class InstructExecutor:
    room_resource_map = {}

    def init_room_resource(self, room_id: int, card_resource: CardResource,
                           coin_resource: CoinResource, player_resource: PlayerResource):
        self.room_resource_map[room_id] = {
            "card": card_resource,
            "coin": coin_resource,
            "player": player_resource
        }

    async def execute(self, room_id: int, player_id: int, instruct: dict, broadcast=None):
        if self.room_resource_map[room_id]['player'].resource[player_id]['can_action'] != UserConst.ACTION_CAN:
            if broadcast:
                await broadcast({"message": "还未到玩家回合，无法行动", "player_id": player_id}, room_id)
            return

        if "instruct" not in instruct:
            if broadcast:
                await broadcast({"message": "缺少指令，key: instruct", "player_id": player_id}, room_id)
            return

        if self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys'][instruct['instruct']] \
                != UserConst.ACTION_CAN:
            if broadcast:
                await broadcast({"message": f"玩家每回合每个指令只能行动一次， instruct: {instruct['instruct']}",
                                 "player_id": player_id}, room_id)
            return

        if instruct['instruct'] == 'buy_card':
            if await self.check_player_can_buy_card(room_id, player_id, instruct.get('card_level'),
                                                    instruct.get('card_type'),
                                                    instruct.get('card_num'), broadcast):
                await self.execute_player_buy_card(room_id, player_id, instruct.get('card_level'),
                                                   instruct.get('card_type'),
                                                   instruct.get('card_num'))
                if broadcast:
                    await broadcast({"message": "买卡成功", "player_id": player_id}, room_id)
                self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys'][
                    'buy_card'] = UserConst.ACTION_NO
                self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys'][
                    'withhold_card'] = UserConst.ACTION_NO
        elif instruct['instruct'] == 'withhold_card':
            if await self.check_player_can_withhold_card(room_id, player_id, instruct.get('card_level'),
                                                         instruct.get('card_type'), instruct.get('card_num'),
                                                         instruct.get('take_gold', 1), broadcast):
                await self.execute_player_withhold_card(room_id, player_id, instruct.get('card_level'),
                                                        instruct.get('card_type'), instruct.get('card_num'),
                                                        instruct.get('take_gold', 1))
                if broadcast:
                    await broadcast({"message": "扣卡成功", "player_id": player_id}, room_id)

                self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys'][
                    'buy_card'] = UserConst.ACTION_NO
                self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys'][
                    'withhold_card'] = UserConst.ACTION_NO
        elif instruct['instruct'] == 'take_coin':
            if await self.check_player_can_take_coin(room_id, player_id, instruct.get('coin_color_list'), broadcast):
                await self.execute_player_take_coin(room_id, player_id, instruct.get('coin_color_list'))
                if broadcast:
                    await broadcast({"message": "拿币成功", "player_id": player_id}, room_id)
                self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys'][
                    'take_coin'] = UserConst.ACTION_NO
        elif instruct['instruct'] == 'pass':
            await self.execute_player_pass(room_id, player_id)
            if broadcast:
                await broadcast({"message": "玩家跳过行动", "player_id": player_id}, room_id)
            self.room_resource_map[room_id]['player'].resource[player_id]['instruct_keys']['pass'] = UserConst.ACTION_NO
        else:
            if broadcast:
                await broadcast({"message": f"无效指令: instruct: {instruct['instruct']}", "player_id": player_id}, room_id)

    async def check_player_can_buy_card(self, room_id, player_id, card_level, card_type, card_num, broadcast=None):
        if any([n is None for n in [card_type, card_num]]):
            if broadcast:
                await broadcast({"message": "缺少必须指令: [card_type, card_num]", "player_id": player_id}, room_id)
            return False
        # 只能买明牌或手里扣留的牌
        if card_type not in {CardConst.TYPE_OPEN_CARD, CardConst.TYPE_WITHHOLDING_CARD}:
            if broadcast:
                await broadcast({"message": "只能买明牌或手里扣留的牌", "player_id": player_id}, room_id)
            return False
        if card_type == CardConst.TYPE_WITHHOLDING_CARD:
            try:
                card = self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD][
                    card_num]
            except IndexError:
                card = None
        else:
            card = self.room_resource_map[room_id]['card'].get_card_info(card_level, card_type, card_num)

        if not card:
            if broadcast:
                await broadcast({"message": "选择的牌不存在", "player_id": player_id}, room_id)
            return False

        lack_of_funds = 0
        for k, v in card.card_price.items():
            _lack_of_funds = 0
            bought_card = len([n for n in self.room_resource_map[room_id]['player'].resource[player_id]['card'][k][
                CardConst.TYPE_BOUGHT_CARD] if n is not None])
            if bought_card > v:
                continue

            _lack_of_funds = self.room_resource_map[room_id]['player'].resource[player_id]['coin'][k][
                                 CoinConst.COUNT] - (
                                     v - bought_card)
            if _lack_of_funds < 0:
                lack_of_funds += abs(_lack_of_funds)

        if not lack_of_funds:
            return True
        elif lack_of_funds and lack_of_funds <= \
                self.room_resource_map[room_id]['player'].resource[player_id]['coin'][CoinConst.COLOR_GOLD][
                    CoinConst.COUNT]:
            return True

        if broadcast:
            await broadcast({"message": "玩家无法支付足够的硬币", "player_id": player_id}, room_id)
        return False

    async def execute_player_buy_card(self, room_id, player_id, card_level, card_type, card_num):
        if card_type == CardConst.TYPE_WITHHOLDING_CARD:
            card = self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD][
                card_num]
        else:
            card = self.room_resource_map[room_id]['card'].get_card_info(card_level, card_type, card_num)

        lack_of_funds = 0
        for k, v in card.card_price.items():
            _lack_of_funds = 0
            bought_card = len([n for n in self.room_resource_map[room_id]['player'].resource[player_id]['card'][k][
                CardConst.TYPE_BOUGHT_CARD] if n is not None])
            if bought_card > v:
                continue

            need_pay = v - bought_card
            _lack_of_funds = self.room_resource_map[room_id]['player'].resource[player_id]['coin'][k][
                                 CoinConst.COUNT] - need_pay
            # 钱不足，玩家钱加回币池并清空自身，
            if _lack_of_funds < 0:
                lack_of_funds += abs(_lack_of_funds)
                add_num = self.room_resource_map[room_id]['player'].resource[player_id]['coin'][k][CoinConst.COUNT]

                self.room_resource_map[room_id]['player'].resource[player_id]['coin'][k][CoinConst.COUNT] = 0
                self.room_resource_map[room_id]['coin'].resource[k][CoinConst.COUNT] += add_num

            # 钱够，直接减去需要的钱数
            self.room_resource_map[room_id]['player'].resource[player_id]['coin'][k][CoinConst.COUNT] -= need_pay
            self.room_resource_map[room_id]['coin'].resource[k][CoinConst.COUNT] += need_pay

        if lack_of_funds:
            # 使用金币支付剩余欠款
            self.room_resource_map[room_id]['player'].resource[player_id]['coin'][CoinConst.COLOR_GOLD][
                CoinConst.COUNT] -= lack_of_funds

        # 将卡片加入玩家卡池
        self.room_resource_map[room_id]['player'].resource[player_id]['card'][card.card_color][
            CardConst.TYPE_BOUGHT_CARD].append(card)
        if card_type == CardConst.TYPE_WITHHOLDING_CARD:
            self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD][
                card_num] = None
        else:
            # 将牌取下牌桌
            self.room_resource_map[room_id]['card'].take_card(card_level, card_type, card_num)

        return True

    async def check_player_can_take_coin(self, room_id, player_id, coin_color_list, broadcast=None):
        if coin_color_list is None:
            if broadcast:
                await broadcast({"message": "缺少必须指令: [coin_color_list]", "player_id": player_id}, room_id)
            return False
        if len(coin_color_list) > CoinConst.ROLE_ACTION_MAX_DIFF_COIN:
            if broadcast:
                await broadcast(
                    {"message": f"超出回合内最大可拿数量: {CoinConst.ROLE_ACTION_MAX_DIFF_COIN}", "player_id": player_id}, room_id)
            return False
        # 不能主动拿金币
        if CoinConst.COLOR_GOLD in coin_color_list:
            if broadcast:
                await broadcast({"message": "不能主动拿取金币", "player_id": player_id}, room_id)
            return False

        coin_sum = 0
        for k, v in self.room_resource_map[room_id]['player'].resource[player_id]['coin'].items():
            if k == CoinConst.COLOR_GOLD:
                continue
            coin_sum += v[CoinConst.COUNT]

        if coin_sum + len(coin_color_list) > CoinConst.ROLE_PLAYER_MAX_COIN:
            if broadcast:
                await broadcast({"message": f"超出可拿取硬币总数: {CoinConst.ROLE_PLAYER_MAX_COIN}", "player_id": player_id},
                                room_id)
            return False

        for k, v in self.room_resource_map[room_id]['coin'].resource.items():
            same_coin_num = len(list(filter(lambda n: n == k, coin_color_list)))
            if same_coin_num > CoinConst.ROLE_ACTION_MAX_SAME_COIN:
                if broadcast:
                    await broadcast({"message": f"超出回合内可拿取相同颜色硬币总数: {CoinConst.ROLE_ACTION_MAX_SAME_COIN},"
                                                f"颜色: {k}", "player_id": player_id}, room_id)
                return False

            if same_coin_num == CoinConst.ROLE_ACTION_MAX_SAME_COIN and same_coin_num < len(coin_color_list):
                if broadcast:
                    await broadcast({"message": f"不符合游戏规则，一回合拿取两枚同色币后不能拿其他币了", "player_id": player_id}, room_id)
                return False

            if same_coin_num > v[CoinConst.COUNT]:
                if broadcast:
                    await broadcast({"message": f"超出币池剩余数量无法拿取, 颜色: {k}", "player_id": player_id}, room_id)
                return False

        return True

    async def execute_player_take_coin(self, room_id, player_id, coin_color_list):
        for c in coin_color_list:
            self.room_resource_map[room_id]['coin'].resource[c][CoinConst.COUNT] -= 1
            self.room_resource_map[room_id]['player'].resource[player_id]['coin'][c][CoinConst.COUNT] += 1

    async def check_player_can_withhold_card(self, room_id, player_id, card_level, card_type, card_num, take_gold,
                                             broadcast=None):
        if not any([n is None for n in [card_level, card_type, card_num]]):
            if broadcast:
                await broadcast({"message": "缺少必须指令: [card_level, card_type, card_num]", "player_id": player_id},
                                room_id)
            return False

        if card_level not in {CardConst.LEVEL_1_CARD, CardConst.LEVEL_2_CARD, CardConst.LEVEL_3_CARD}:
            if broadcast:
                await broadcast({"message": f"卡片等级必须在[{CardConst.LEVEL_1_CARD},"
                                            f" {CardConst.LEVEL_2_CARD},"
                                            f" {CardConst.LEVEL_3_CARD}]中",
                                 "player_id": player_id}, room_id)
            return False

        if card_type not in {CardConst.TYPE_OPEN_CARD, CardConst.TYPE_DARK_CARD}:
            if broadcast:
                await broadcast({"message": f"卡片类型必须是{CardConst.TYPE_OPEN_CARD}或{CardConst.TYPE_DARK_CARD}",
                                 "player_id": player_id}, room_id)
            return False

        if len([n for n in
                self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD] if n]) \
                > CardConst.ROLE_MAX_WITHHOLDING_CARD:
            if broadcast:
                await broadcast({"message": "玩家扣卡数不能超过: {CardConst.ROLE_MAX_WITHHOLDING_CARD}",
                                 "player_id": player_id}, room_id)
            return False

        coin_sum = 0
        for k, v in self.room_resource_map[room_id]['player'].resource[player_id]['coin'].items():
            if k == CoinConst.COLOR_GOLD:
                continue
            coin_sum += v[CoinConst.COUNT]

        gold_num = 0
        if take_gold:
            if self.room_resource_map[room_id]['coin'].resource[CoinConst.COLOR_GOLD][CoinConst.COUNT] > 0:
                gold_num += 1
            else:
                if broadcast:
                    await broadcast({"message": "剩余金币数不足，加入指令: [take_gold=0] 可不拿金币",
                                     "player_id": player_id}, room_id)
                return False

        if coin_sum + gold_num > CoinConst.ROLE_PLAYER_MAX_COIN:
            if broadcast:
                await broadcast({"message": f"超出可拿取硬币总数: {CoinConst.ROLE_PLAYER_MAX_COIN}",
                                 "player_id": player_id}, room_id)
            if gold_num > 0:
                if broadcast:
                    await broadcast({"message": "加入指令: [take_gold=0] 可不拿金币",
                                     "player_id": player_id}, room_id)

            return False

        card = self.room_resource_map[room_id]['card'].get_card_info(card_level, card_type, card_num)
        if not card:
            if broadcast:
                await broadcast({"message": "卡片获取失败", "player_id": player_id}, room_id)
            return False

        return True

    async def execute_player_withhold_card(self, room_id, player_id, card_level, card_type, card_num, take_gold):
        # 牌池取出卡片
        card = self.room_resource_map[room_id]['card'].take_card(card_level, card_type, card_num)
        # 玩家扣牌区加入卡片，获取第一个为None的index，如果不存在则向后追加
        index = -1
        for i, c in enumerate(
                self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD]):
            if not c:
                index = i
                break
        if index >= 0:
            self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD][index] = card
        else:
            self.room_resource_map[room_id]['player'].resource[player_id][CardConst.TYPE_WITHHOLDING_CARD].append(card)
        # 如果取金币，金币池-1, 玩家金币+1
        if take_gold:
            self.room_resource_map[room_id]['coin'].resource[CoinConst.COLOR_GOLD][CoinConst.COUNT] -= 1
            self.room_resource_map[room_id]['player'].resource[player_id]['coin'][CoinConst.COLOR_GOLD][
                CoinConst.COUNT] += 1

    async def execute_player_pass(self, room_id, player_id):
        self.room_resource_map[room_id]['player'].resource[player_id]['can_action'] = UserConst.ACTION_NO


instruct_executor = InstructExecutor()
