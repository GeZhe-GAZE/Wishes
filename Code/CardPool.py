r"""
Wishes v3.0
-----------

Module
_
    CardPool

Description
_
    CardPool 卡池类型定义
    集成抽卡逻辑、卡组管理和抽卡记录
"""


from Base import *
from WishLogic import WishLogic, reset_logic
from WishRecorder import WishRecorder


class CardPool:
    """
    卡池类
    集成抽卡逻辑、卡组管理、抽卡记录三部分功能
    """
    def __init__(self, name: str, logic: WishLogic, card_group: CardGroup, recorder_dir: str) -> None:
        self.name = name
        self.logic = logic
        self.card_group = card_group
        self.recorder = WishRecorder(recorder_dir)

    def wish_one(self) -> WishResult:
        """
        单抽
        """
        logic_res = self.logic.wish_one()
        result = WishResult()

        card = self.card_group.random_card(logic_res.is_up, logic_res.star, logic_res.type)
        result.add(card)
        self.recorder.add_record(card)

        return result
    
    def wish_ten(self) -> WishResult:
        """
        十连
        """
        result = WishResult()

        for _ in range(10):
            logic_res = self.logic.wish_one()
            card = self.card_group.random_card(logic_res.is_up, logic_res.star, logic_res.type)
            result.add(card)
            self.recorder.add_record(card)

        return result
    
    def reset(self):
        """
        重置卡池
        """
        self.logic = reset_logic(self.logic)
        self.recorder.clear()
    
    def end(self):
        """
        程序退出操作
        """
        self.recorder._write_file()
