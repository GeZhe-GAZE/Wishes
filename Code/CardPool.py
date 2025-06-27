r"""
Wishes v3.0
-----------

Module
_
    CardPool

Description
_
    CardPool 卡池类型定义
    集成 抽卡逻辑、卡组管理 和 抽卡记录 功能
"""


from Base import *
from WishRule import WishLogic
from WishRecorder import WishRecorder


class CardPool:
    """
    卡池类
    集成抽卡逻辑、卡组管理、抽卡记录三部分功能
    """
    def __init__(self, name: str, logic: WishLogic, card_group: CardGroup, recorder_dir: str, none_flag: bool = False) -> None:
        self.none_flag = none_flag
        if none_flag:
            return
        self.name = name
        self.logic = logic
        self.card_group = card_group
        self.recorder = WishRecorder(recorder_dir, self.card_group.max_star)

    def wish_one(self) -> WishResult:
        """
        单抽
        """
        result = WishResult()

        logic_result = self.logic.wish()

        card = self.card_group.random_card(logic_result.type_, logic_result.star, logic_result.tag)
        packed_card = PackedCard(card, logic_result.tag)
        result.add(packed_card)
        self.recorder.add_record(packed_card)

        return result
    
    def wish_ten(self) -> WishResult:
        """
        十连
        """
        result = WishResult()

        for _ in range(10):
            logic_result = self.logic.wish()
            card = self.card_group.random_card(logic_result.type_, logic_result.star, logic_result.tag)
            packed_card = PackedCard(card, logic_result.tag)
            result.add(packed_card)
            self.recorder.add_record(packed_card)

        return result
    
    def wish_count(self, count: int) -> WishResult:
        """
        指定次数抽卡
        """
        result = WishResult()

        for _ in range(count):
            logic_result = self.logic.wish()
            card = self.card_group.random_card(logic_result.type_, logic_result.star, logic_result.tag)
            packed_card = PackedCard(card, logic_result.tag)
            result.add(packed_card)
            self.recorder.add_record(packed_card)

        return result
    
    def reset(self, with_records: bool = True):
        """
        重置卡池
        with_records: 是否重置抽卡记录
        """
        self.logic.reset()
        if with_records:
            self.recorder.clear()
    
    def get_logic_state(self) -> Dict:
        """
        获取当前逻辑状态
        """
        state = {}
        self.logic.reg_state(state)
        return state

    def set_logic_state(self, state: Dict):
        """
        设置逻辑状态
        """
        self.logic.load_state(state)
    
    # def end(self):
    #     """
    #     程序退出操作
    #     """
    #     self.recorder._write_file()

    @staticmethod
    def none() -> 'CardPool':
        return CardPool("None", WishLogic.none(), CardGroup("empty"), "", none_flag=True)
