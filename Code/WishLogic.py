r"""
Wishes v3.0
-----------

Module
_
    WishLogic

Description
_
    定义不同卡池的抽卡算法
    是 Wishes 的核心算法模块
"""


from Base import *
from Const import *
from random import randint, choices
from abc import ABC, abstractmethod


# class LogicResult:
#     def __init__(self, star: int, is_up: bool, type_: str):
#         self.star = star
#         self.is_up = is_up
#         self.type = type_


class WishLogic(ABC):
    """
    抽卡逻辑抽象基类，定义一个抽卡逻辑所需具备的属性和方法，不实现具体逻辑
    """
    def __init__(self):
        self.counter: dict[int, int] = {
            5: 0,       # 五星抽卡计数
            4: 0,       # 四星抽卡计数
        }
        self.max_counter: dict[int, int] = {
            5: 90,      # 五星保底次数
            4: 10,      # 四星保底次数
        }
        self.base_probability: dict[int, int] = {
            5: 60,      # 五星概率
            4: 510,     # 四星概率
                        # 三星概率自动计算
        }               # 补充说明：Wishes 的概率使用整数表示，以避免浮点数带来的精度误差，实际概率为整数值的万分之一
        self.probability: dict[int, int] = {        # 实时概率
            5: self.base_probability[5],
            4: self.base_probability[4],
            3: max(MAX_PROBABILITY - self.base_probability[5] - self.base_probability[4], 0),
        }
        self.step_probability: dict[int, int] = {   # 概率提升步长，五星在第 73/63 抽后开始提升，四星在第 9 抽
            5: 600,
            4: 5100,
        }
        self.next_up: dict[int, int] = {
            5: False,
            4: False,
        }
    
    @abstractmethod
    def update_probability(self):
        """
        概率更新机制
        """
        pass
    
    @abstractmethod
    def _wish_5(self) -> LogicResult:
        """
        抽出五星逻辑
        """
        pass

    @abstractmethod
    def _wish_4(self) -> LogicResult:
        """
        抽出四星逻辑
        """
        pass

    @abstractmethod
    def _wish_3(self) -> LogicResult:
        """
        抽出三星逻辑
        """
        pass

    @abstractmethod
    def wish_one(self) -> LogicResult:
        """
        单抽逻辑
        """
        pass


class RoleLogic(WishLogic):
    """
    角色卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()
        self.next_4_role = False        # 四星出武器后必出角色

    def update_probability(self):
        if self.counter[5] >= 73:
            self.probability[5] += self.step_probability[5]
        # 五星小保底
        if self.counter[5] >= 90:
            self.probability[5] = MAX_PROBABILITY
        
        if self.counter[4] >= 9:
            self.probability[4] += self.step_probability[4]
        # 四星保底
        if self.counter[4] >= 10:
            self.probability[4] = MAX_PROBABILITY - self.probability[5]

    def _wish_5(self) -> LogicResult:
        if self.next_up[5]:
            res =  LogicResult(5, True, TYPE_ROLE)
        else:
            is_up = randint(0, 1)   # 歪/不歪
            res = LogicResult(5, bool(is_up), TYPE_ROLE)
        
        self.next_up[5] = not res.is_up
        self.counter[5] = 0
        self.probability[5] = self.base_probability[5]
        return res
    
    def _wish_4(self) -> LogicResult:
        if self.next_up[4]:
            res = LogicResult(4, True, TYPE_ROLE)
        else:
            is_role = 1 if self.next_4_role else randint(0, 1)     # 武器/角色
            if is_role:
                is_up = randint(0, 1)
                res = LogicResult(4, bool(is_up), TYPE_ROLE)
            else:
                res = LogicResult(4, False, TYPE_WEAPON)
        
        self.next_up[4] = not res.is_up
        self.next_4_role = res.type == TYPE_WEAPON
        self.counter[4] = 0
        self.probability[4] = self.base_probability[4]
        return res

    def _wish_3(self) -> LogicResult:
        return LogicResult(3, False, TYPE_WEAPON)
    
    def wish_one(self) -> LogicResult:
        self.counter[5] += 1
        self.counter[4] += 1

        self.update_probability()

        p = (   # 实际概率计算
            self.probability[5],
            max(min(MAX_PROBABILITY - self.probability[5], self.probability[4]), 0),
            max(MAX_PROBABILITY - self.probability[5] - self.probability[4], 0)
        )

        star = choices((5, 4, 3), weights=p)[0]     # 返回列表，索引取值
        if star == 5:
            res = self._wish_5()
        elif star == 4:
            res = self._wish_4()
        else:
            res = self._wish_3()
        
        return res


class WeaponLogic(WishLogic):
    """
    武器卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()

    def update_probability(self):
        if self.counter[5] >= 73:
            self.probability[5] += self.step_probability[5]
        # 五星小保底
        if self.counter[5] >= 80:
            self.probability[5] = MAX_PROBABILITY
        
        if self.counter[4] >= 9:
            self.probability[4] += self.step_probability[4]
        # 四星保底
        if self.counter[4] >= 10:
            self.probability[4] = MAX_PROBABILITY - self.probability[5]

    def _wish_5(self) -> LogicResult:
        if self.next_up[5]:
            res =  LogicResult(5, True, TYPE_ROLE)
        else:
            is_up = randint(0, 1)   # 歪/不歪
            res = LogicResult(5, bool(is_up), TYPE_ROLE)
        
        self.next_up[5] = not res.is_up
        self.counter[5] = 0
        self.probability[5] = self.base_probability[5]
        return res
    
    def _wish_4(self) -> LogicResult:
        if self.next_up[4]:
            res = LogicResult(4, True, TYPE_ROLE)
        else:
            is_role = 1 if self.next_4_role else randint(0, 1)     # 武器/角色
            if is_role:
                is_up = randint(0, 1)
                res = LogicResult(4, bool(is_up), TYPE_ROLE)
            else:
                res = LogicResult(4, False, TYPE_WEAPON)
        
        self.next_up[4] = not res.is_up
        self.next_4_role = res.type == TYPE_WEAPON
        self.counter[4] = 0
        self.probability[4] = self.base_probability[4]
        return res

    def _wish_3(self) -> LogicResult:
        return LogicResult(3, False, TYPE_WEAPON)
    
    def wish_one(self) -> LogicResult:
        self.counter[5] += 1
        self.counter[4] += 1

        self.update_probability()

        p = (   # 实际概率计算
            self.probability[5],
            max(min(MAX_PROBABILITY - self.probability[5], self.probability[4]), 0),
            max(MAX_PROBABILITY - self.probability[5] - self.probability[4], 0)
        )

        star = choices((5, 4, 3), weights=p)[0]     # 返回列表，索引取值
        if star == 5:
            res = self._wish_5()
        elif star == 4:
            res = self._wish_4()
        else:
            res = self._wish_3()
        
        return res


class GenshinRoleLogic(RoleLogic):
    """
    原神角色卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()


class GenshinWeaponLogic(WeaponLogic):
    """
    原神武器卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()


class StarRailRoleLogic(RoleLogic):
    """
    崩铁角色卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()


class StarRailWeaponLogic(WeaponLogic):
    """
    崩铁武器卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()


class ZZZRoleLogic(RoleLogic):
    """
    绝区零角色卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()
        self.base_probability[4] = 940
        self.probability[4] = 940
    
    def _wish_4(self) -> LogicResult:
        # 绝区零角色池四星人物与武器概率不一，进行特殊处理
        if self.next_up[4]:
            res = LogicResult(4, True, TYPE_ROLE)
        else:
            # 角色 / 武器
            # 7.05% / 2.35%
            is_role = 1 if self.next_4_role else choices((1, 0), weights=(705, 235))
            if is_role:
                is_up = randint(0, 1)
                res = LogicResult(4, bool(is_up), TYPE_ROLE)
            else:
                res = LogicResult(4, False, TYPE_WEAPON)
        
        self.next_up[4] = not res.is_up
        self.next_4_role = res.type == TYPE_WEAPON
        self.counter[4] = 0
        self.probability[4] = self.base_probability[4]
        return res


class ZZZWeaponLogic(WeaponLogic):
    """
    绝区零武器卡池抽卡逻辑
    """
    def __init__(self):
        super().__init__()


def new_logic(game: str, type_: str) -> WishLogic:
    t = (game, type_)
    if t == (GAME_GENSHIN, TYPE_ROLE):
        return GenshinRoleLogic()
    if t == (GAME_GENSHIN, TYPE_WEAPON):
        return GenshinWeaponLogic()
    if t == (GAME_STAR_RAIL, TYPE_ROLE):
        return StarRailRoleLogic()
    if t == (GAME_STAR_RAIL, TYPE_WEAPON):
        return StarRailWeaponLogic()
    if t == (GAME_ZZZ, TYPE_ROLE):
        return ZZZRoleLogic()
    if t == (GAME_ZZZ, TYPE_WEAPON):
        return ZZZWeaponLogic()
    return RoleLogic()


def reset_logic(logic: WishLogic) -> WishLogic:
    return logic.__class__()
    