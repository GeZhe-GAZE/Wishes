r"""
Wishes v3.0
-----------

Module
_
    WishRule

Description
_
    Wishes 核心模块
    不同抽卡机制的模块化实现
    目的是实现卡池抽卡机制的可定制化
"""


from Base import *
from Const import *
from abc import abstractmethod, ABC
from typing import List, Dict, Type, Tuple, Optional
from copy import deepcopy
import random


class RuleContext:
    """
    规则执行上下文
    """
    def __init__(self) -> None:
        # 当前抽逻辑结果
        self.result: Optional[LogicResult] = None
        # 规则通讯桥梁, 可通过规则 tag 名称访问规则对象
        self.rule_bridge: Dict[str, BaseRule] = {}

        # 当前抽实际结果
        self.packed_card_result: Optional[PackedCard] = None


class BaseRule(ABC):
    """
    规则基类
    """
    # 规则标识符
    tag: str = "BaseRule"

    def __init__(self, **kwargs):
        """
        初始化
        注意: 传入的配置字典是由 json 直接解析得到的字典, 这意味着所有的键都是字符串类型
        """
        super().__init__()
    
    @abstractmethod
    def set_bridge(self, ctx: RuleContext):
        """
        初始化时，在上下文中注册规则对象
        """
        pass

    @abstractmethod
    def apply(self, ctx: RuleContext):
        """
        每次抽卡时具体执行的逻辑
        """
        pass
    
    @abstractmethod
    def callback(self, ctx: RuleContext):
        """
        每次抽卡结束后的回调操作
        """
        pass

    @abstractmethod
    def reset(self, ctx: RuleContext):
        """
        重置规则状态
        """
        pass
    
    @abstractmethod
    def load_state(self, state: Dict):
        """
        从状态字典中加载规则状态
        状态字典中的星级键使用字符串类型
        """
        pass
    
    @abstractmethod
    def reg_state(self, state: Dict):
        """
        注册规则状态
        """
        pass


class StarCounterRule(BaseRule):
    """
    星级计数器规则
    提供每个星级的抽卡计数，计数器会在抽出对应星级后重置
    所有操作在回调函数中完成
    """
    tag: str = "StarCounterRule"

    def __init__(self, star_list: List[int] ,**kwargs):
        """
        星级计数器初始化为 0
        由于计数器在回调过程中更新
        因此，当前实际抽数是 计数器值 + 1
        故各类型在使用本规则的计数器时需自加 1
        """
        self.star_counter: Dict[int, int] = {
            star: 0 
            for star in star_list
        }

    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        不操作
        """
    
    def callback(self, ctx: RuleContext):
        """
        回调中，更新星级计数器
        """
        for star in self.star_counter.keys():
            self.star_counter[star] += 1
        
        if ctx.result and ctx.result.star:
            self.star_counter[ctx.result.star] = 0
        
    def reset(self, ctx: RuleContext):
        """
        重置星级计数器
        """
        for star in self.star_counter.keys():
            self.star_counter[star] = 0
    
    def load_state(self, state: Dict):
        """
        加载星级计数器状态
        """
        if self.tag not in state:
            return
        
        star_counter_state = state[self.tag].get("star_counter", {})

        for star in self.star_counter.keys():
            self.star_counter[star] = star_counter_state.get(str(star), self.star_counter[star])
    
    def reg_state(self, state: Dict):
        """
        注册星级计数器状态
        """
        star_counter_state = {
            str(star): self.star_counter[star]
            for star in self.star_counter.keys()
        }

        if star_counter_state:
            state[self.tag] = {
                "star_counter": star_counter_state
            }


class TypeStarCounterRule(BaseRule):
    """
    基于星级的类型计数器规则
    提供每个星级下各类型的抽卡计数，计数器会在抽出对应类型后重置
    所有操作在回调函数中完成
    """
    tag: str = "TypeStarCounterRule"

    def __init__(self, type_star_dict: Dict[str, List[str]], **kwargs):
        self.type_star_counter: Dict[int, Dict[str, int]] = {
            int(star): {
                type_: 0 
                for type_ in type_star_dict[star]
            } 
            for star in type_star_dict.keys()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        """
        不操作
        """
    
    def callback(self, ctx: RuleContext):
        """
        回调中，更新类型计数器
        """
        if not ctx.result or not ctx.result.star in self.type_star_counter:
            return

        for type_ in self.type_star_counter[ctx.result.star].keys():
            if type_ == ctx.result.type_:
                self.type_star_counter[ctx.result.star][type_] = 0
                continue
            self.type_star_counter[ctx.result.star][type_] += 1
    
    def reset(self, ctx: RuleContext):
        """
        重置类型计数器
        """
        for star in self.type_star_counter.keys():
            for type_ in self.type_star_counter[star].keys():
                self.type_star_counter[star][type_] = 0
    
    def load_state(self, state: Dict):
        """
        加载类型计数器状态
        """
        if self.tag not in state:
            return

        type_star_counter_state = state[self.tag].get("type_star_counter", {})

        for star, type_counter in self.type_star_counter.items():
            star_string = str(star)
            if star_string not in type_star_counter_state:
                continue

            star_state = type_star_counter_state[star_string]
            for type_ in type_counter.keys():
                type_counter[type_] = star_state.get(type_, type_counter[type_])

    def reg_state(self, state: Dict):
        """
        注册类型计数器状态
        """
        type_star_counter_state = {
            str(star): {
                type_: self.type_star_counter[star][type_]
                for type_ in self.type_star_counter[star].keys()
            }
            for star in self.type_star_counter.keys()
        }

        if type_star_counter_state:
            state[self.tag] = {
                "type_star_counter": type_star_counter_state
            }


class StarProbabilityRule(BaseRule):
    """
    星级基础概率规则
    根据当前星级概率权重决定当前抽星级
    每次回调都会重置概率为基础概率
    """
    tag: str = "StarProbabilityRule"

    def __init__(self, star_probability: Dict[str, int], **kwargs):
        self.base_probability: Dict[int, int] = {
            int(star): probability
            for star, probability in star_probability.items()
        }
        self.star_probability: Dict[int, int] = self.base_probability.copy()
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        根据 star_probability 的概率权重决定星级
        """
        # 若星级已被决定，则不操作
        if ctx.result is None or not ctx.result.star:
            stars = list(self.star_probability.keys())
            weights = list(self.star_probability.values())
            target_star = random.choices(stars, weights=weights)[0]
            ctx.result = LogicResult(star=target_star, type_="")
    
    def callback(self, ctx: RuleContext):
        """
        抽卡结束后重置概率
        """
        self.star_probability = self.base_probability.copy()
    
    def reset(self, ctx: RuleContext):
        """
        重置星级概率
        """
        self.star_probability = self.base_probability.copy()
    
    def load_state(self, state: Dict):
        """
        不操作
        *星级概率无需保存
        """
    
    def reg_state(self, state: Dict):
        """
        不操作
        *星级概率无需保存
        """


class TypeStarProbabilityRule(BaseRule):
    """
    基于星级的类型基础概率规则
    根据当前星级，和星级对应的类型概率权重决定当前抽类型
    """
    tag: str = "TypeStarProbabilityRule"

    def __init__(self, type_probability: Dict[str, Dict[str, int]], **kwargs):
        self.type_probability: Dict[int, Dict[str, int]] = {
            int(star): {
                type_: probability
                for type_, probability in type_probability[star].items()
            }
            for star in type_probability.keys()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        根据星级，获取对应的类型概率权重并决定类型
        """
        # 若类型已决定，则不操作
        if ctx.result is None or not ctx.result.star or ctx.result.type_:
            return
        
        type_weights = self.type_probability.get(ctx.result.star, {})
        types = tuple(type_weights.keys())
        weights = tuple(type_weights.values())
        if types and weights:
            target_type = random.choices(types, weights=weights)[0]
            ctx.result.type_ = target_type
    
    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        pass

    def load_state(self, state: Dict):
        pass

    def reg_state(self, state: Dict):
        pass


class StarPityRule(BaseRule):
    """
    星级保底规则
    提供对应星级的保底，若抽卡次数达到阈值，则触发保底，并重置计数器
    *不同星级的保底触发优先级遵循 star_pity 中设定的星级顺序
    """
    tag: str = "StarPityRule"

    def __init__(self, star_pity: Dict[str, int], reset_lower_pity: bool, **kwargs) -> None:
        self.star_pity: Dict[int, int] = {
            int(star): threshold
            for star, threshold in star_pity.items()
        }
        self.is_pity: Dict[int, bool] = {    # 当前抽各星级是否触发保底
            int(star): False
            for star in self.star_pity.keys()
        }
        self.reset_lower_pity = reset_lower_pity    # 高星级是否重置低星级保底
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        """
        检查星级保底，若触发，则按 star_pity 字典中顺序取最先触发保底星级
        若 星级保底被更大的星级保底覆盖 且 reset_lower_pity 为 True, 则重置该星级保底
        本规则决定的星级优先级大于 StarProbabilityRule
        """
        for star in self.is_pity.keys():
            self.is_pity[star] = False

        star_counter = ctx.rule_bridge[StarCounterRule.tag].star_counter # type: ignore
        for star, threshold in self.star_pity.items():
            counter = star_counter.get(star, 0) + 1
            if counter >= threshold:
                ctx.result = LogicResult(star=star, type_="")
                star_counter[star] = 0
                self.is_pity[star] = True
                return
    
    def callback(self, ctx: RuleContext):
        """
        当 reset_lower_pity 为 True 时, 重置低星级保底
        """
        if not self.reset_lower_pity or ctx.result is None:
            return
        
        cur_star = ctx.result.star

        star_counter: Dict[int, int] = ctx.rule_bridge[StarCounterRule.tag].star_counter # type: ignore
        for star in star_counter.keys():
            if star < cur_star:
                star_counter[star] = 0

    def reset(self, ctx: RuleContext):
        for star in self.is_pity.keys():
            self.is_pity[star] = False

    def load_state(self, state: Dict):
        """
        加载保底状态
        """
        if self.tag not in state:
            return
        
        is_pity = state[self.tag].get("is_pity", {})
        for star in self.is_pity.keys():
            self.is_pity[star] = is_pity.get(str(star), self.is_pity[star])

    def reg_state(self, state: Dict):
        """
        注册保底状态
        """
        is_pity_state = {
            str(star): is_pity
            for star, is_pity in self.is_pity.items()
        }

        if is_pity_state:
            state[self.tag] = {
                "is_pity": is_pity_state
            }


class TypeStarPityRule(BaseRule):
    """
    基于星级的类型保底规则
    提供对应星级的类型保底，若抽卡次数达到阈值，则触发保底，并重置计数器
    *不同类型的保底触发优先级遵循 type_pity 中该星级下设定的类型顺序
    """
    tag: str = "TypeStarPityRule"

    def __init__(self, type_pity: Dict[str, Dict[str, int]], **kwargs) -> None:
        self.type_pity: Dict[int, Dict[str, int]] = {
            int(star): {
                type_: threshold
                for type_, threshold in type_pity[star].items()
            }
            for star in type_pity.keys()
        }
        self.is_pity: Dict[int, Dict[str, bool]] = {    # 当前抽是否触发保底
            star: {
                type_: False
                for type_ in self.type_pity[star].keys()
            }
            for star in self.type_pity.keys()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        根据星级，获取对应的类型保底
        检查该星级各类型保底，若触发，则按 type_pity 字典中顺序取最先触发保底的类型
        若类型已被决定，则将重置该类型保底，且不操作
        本规则决定的类型优先级大于 TypeStarProbabilityRule
        """
        for star in self.is_pity.keys():
            for type_ in self.is_pity[star].keys():
                self.is_pity[star][type_] = False

        if ctx.result is None or not ctx.result.star:
            return

        type_counter = ctx.rule_bridge[TypeStarCounterRule.tag].type_star_counter # type: ignore
        # 星级不包含在保底列表内，不操作
        if ctx.result.star not in self.type_pity:
            return
        # 类型已决定，更新计数器，不操作
        if ctx.result.type_:
            if ctx.result.type_ in type_counter[ctx.result.star]:
                type_counter[ctx.result.star][ctx.result.type_] = 0
            return
        # 通过保底决定类型
        for type_, threshold in self.type_pity[ctx.result.star].items():
            counter = type_counter.get(ctx.result.star, {}).get(type_, 0)
            if counter >= threshold:
                ctx.result.type_ = type_
                type_counter[ctx.result.star][type_] = 0
                self.is_pity[ctx.result.star][type_] = True
                return
    
    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        for star in self.is_pity.keys():
            for type_ in self.is_pity[star].keys():
                self.is_pity[star][type_] = False

    def load_state(self, state: Dict):
        """
        加载 is_pity 保底状态
        """
        if self.tag not in state:
            return

        is_pity = state[self.tag].get("is_pity", {})
        for star in self.is_pity.keys():
            if star not in is_pity:
                continue
            for type_ in self.is_pity[star].keys():
                self.is_pity[star][type_] = is_pity[star].get(type_, self.is_pity[star][type_])

    def reg_state(self, state: Dict):
        """
        注册 is_pity 保底状态
        """
        is_pity_state = {
            str(star): {
                type_: is_pity
                for type_, is_pity in self.is_pity[star].items()
            }
            for star in self.is_pity.keys()
        }

        if is_pity_state:
            state[self.tag] = {
                "is_pity": is_pity_state
            }


class UpRule(BaseRule):
    """
    UP 规则
    将 UP 卡片设定为拥有显著高于同星级基础概率的抽取出现率的规则
    同时附带对 UP 卡片的计数器和保底机制
    """
    tag: str = "UpRule"

    def __init__(self, up_probability: Dict[str, int], up_pity: Dict[str, int] ,**kwargs) -> None:
        self.up_probability: Dict[int, int] = {
            int(star): probability
            for star, probability in up_probability.items()
        }
        self.up_pity: Dict[int, int] = {
            int(star): pity
            for star, pity in up_pity.items()
        }
        self.up_counter: Dict[int, int] = {
            star: 0
            for star in self.up_probability.keys()
        }
        self.is_up_pity: Dict[int, bool] = {    # 当前抽是否触发 UP 保底
            star: False
            for star in self.up_pity.keys()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        """
        根据星级，获取对应的 UP 保底
        若触发保底则决定为 UP
        若未触发，则根据 up_probability 中指定的对应星级的 UP 概率权重决定是否 UP
        """
        for star in self.is_up_pity.keys():
            self.is_up_pity[star] = False

        if ctx.result is None or ctx.result.star not in self.up_probability:
            return
        
        counter = self.up_counter[ctx.result.star]
        if ctx.result.star in self.up_pity and counter >= self.up_pity[ctx.result.star]:    # 触发 UP 保底
            ctx.result.tags.append(TAG_UP)
            self.up_counter[ctx.result.star] = 0
            self.is_up_pity[ctx.result.star] = True
        else:
            up_weight = self.up_probability[ctx.result.star]
            if random.choices((True, False), (up_weight, MAX_PROBABILITY - up_weight))[0]:  # 正常抽取 UP
                ctx.result.tags.append(TAG_UP)

            if TAG_UP in ctx.result.tags:
                self.up_counter[ctx.result.star] = 0
            else:
                self.up_counter[ctx.result.star] += 1
    
    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        """
        重置 up_counter 计数器和 is_up_pity 保底状态
        """
        self.up_counter = {
            star: 0
            for star in self.up_probability.keys()
        }
        for star in self.is_up_pity.keys():
            self.is_up_pity[star] = False
    
    def load_state(self, state: Dict):
        """
        加载 up_counter 计数器和 is_up_pity 保底状态
        """
        if self.tag not in state:
            return
        
        up_counter_state = state[self.tag].get("up_counter", {})
        for star in self.up_counter.keys():
            self.up_counter[star] = up_counter_state.get(str(star), self.up_counter[star])
        
        is_up_pity_state = state[self.tag].get("is_up_pity", {})
        for star in self.is_up_pity.keys():
            self.is_up_pity[star] = is_up_pity_state.get(str(star), self.is_up_pity[star])
    
    def reg_state(self, state: Dict):
        """
        注册 up_counter 计数器和 is_up_pity 保底状态
        """
        up_counter_state = {
            str(star): self.up_counter[star]
            for star in self.up_counter.keys()
        }
        is_up_pity_state = {
            str(star): self.is_up_pity[star]
            for star in self.is_up_pity.keys()
        }

        if up_counter_state or is_up_pity_state:
            state[self.tag] = {}

            if up_counter_state:
                state[self.tag]["up_counter"] = up_counter_state
            
            if is_up_pity_state:
                state[self.tag]["is_up_pity"] = is_up_pity_state


class UpTypeRule(BaseRule):
    """
    UP 类型分布规则
    在同星级的 UP 卡片内部，支持设定不同类型的 UP 卡片概率权重的规则
    同时附带基于星级的对 UP 类型的计数器和保底机制
    """
    tag: str = "UpTypeRule"

    def __init__(self, up_type_probability: Dict[str, Dict[str, int]], up_type_pity: Dict[str, Dict[str, int]], **kwargs):
        self.up_type_probability: Dict[int, Dict[str, int]] = {
            int(star): {
                type_: probability
                for type_, probability in up_type_probability[star].items()
            }
            for star in up_type_probability.keys()
        }
        self.up_type_pity: Dict[int, Dict[str, int]] = {
            int(star): {
                type_: pity
                for type_, pity in up_type_pity[star].items()
            }
            for star in up_type_pity.keys()
        }
        self.up_type_counter = {
            star: {
                type_: 0
                for type_ in self.up_type_pity[star].keys()
            }
            for star in self.up_type_pity.keys()
        }
        self.is_up_type_pity = {
            star: {
                type_: False
                for type_ in self.up_type_pity[star].keys()
            }
            for star in self.up_type_pity.keys()
        }

    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        """
        在当前为 UP 的情况下，根据概率权重决定类型
        所有可 UP 类型及对应权重由 up_type_probability 指定
        """
        for star in self.is_up_type_pity.keys():
            for type_ in self.is_up_type_pity[star].keys():
                self.is_up_type_pity[star][type_] = False

        if ctx.result is None or ctx.result.star not in self.up_type_probability or TAG_UP not in ctx.result.tags:
            return
        
        if ctx.result.star in self.up_type_pity:
            counter = self.up_type_counter[ctx.result.star]
            for type_ in counter.keys():
                counter[type_] += 1

            for type_ in counter.keys():
                if counter[type_] > self.up_type_pity[ctx.result.star][type_]:     # 触发 UP 类型保底
                    ctx.result.type_ = type_
                    counter[type_] = 0
                    self.is_up_type_pity[ctx.result.star][type_] = True
                    return
        
        types = tuple(self.up_type_probability[ctx.result.star].keys())
        weights = tuple(self.up_type_probability[ctx.result.star].values())
        ctx.result.type_ = random.choices(types, weights=weights)[0]

    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        """
        重置 up_type_counter 计数器和 is_up_type_pity 保底状态
        """
        self.up_type_counter = {
            star: {
                type_: 0 
                for type_ in self.up_type_probability[star].keys()
            }
            for star in self.up_type_probability.keys()
        }
        for star in self.is_up_type_pity.keys():
            for type_ in self.is_up_type_pity[star].keys():
                self.is_up_type_pity[star][type_] = False
    
    def load_state(self, state: Dict):
        """
        加载 up_type_counter 计数器和 is_up_type_pity 保底状态
        """
        if self.tag not in state:
            return

        up_type_counter_state = state[self.tag].get("up_type_counter", {})

        for star in self.up_type_counter.keys():
            for type_ in self.up_type_counter[star].keys():
                self.up_type_counter[star][type_] = up_type_counter_state.get(str(star), {}).get(type_, self.up_type_counter[star][type_])
        
        is_up_type_pity_state = state[self.tag].get("is_up_type_pity", {})
        for star in self.is_up_type_pity.keys():
            for type_ in self.is_up_type_pity[star].keys():
                self.is_up_type_pity[star][type_] = is_up_type_pity_state.get(str(star), {}).get(type_, self.is_up_type_pity[star][type_])

    def reg_state(self, state: Dict):
        """
        注册 up_type_counter 计数器和 is_up_type_pity 保底状态
        """
        up_type_counter_state = {
            str(star): {
                type_: self.up_type_counter[star][type_]
                for type_ in self.up_type_counter[star].keys()
            }
            for star in self.up_type_counter.keys()
        }
        is_up_type_pity_state = {
            str(star): {
                type_: self.is_up_type_pity[star][type_]
                for type_ in self.is_up_type_pity[star].keys()
            }
            for star in self.is_up_type_pity.keys()
        }

        if up_type_counter_state or is_up_type_pity_state:
            state[self.tag] = {}

            if up_type_counter_state:
                state[self.tag]["up_type_counter"] = up_type_counter_state

            if is_up_type_pity_state:
                state[self.tag]["is_up_type_pity"] = is_up_type_pity_state


class StarProbabilityIncreaseRule(BaseRule):
    """
    星级概率增长规则
    在 StarProbabilityRule 的基础上, 实现星级概率从起始值开始随抽数等差增长的规则
    *仅当本规则先于 StarProbabilityRule 执行时生效
    """
    tag: str = "StarProbabilityIncreaseRule"

    def __init__(self, star_increase: Dict[str, Tuple[int, int]],**kwargs) -> None:
        self.star_increase: Dict[int, Tuple[int, int]] = {
            int(star): (start, increment)
            for star, (start, increment) in star_increase.items()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        """
        修改 StarProbabilityRule 的概率权重，实现概率增长
        将检查各星级计数器是否达到概率累加起点
        若达到，则根据超出抽数计算当前抽该星级的概率
        在 star_probability 中顺序越靠前的星级，其概率优先级越高
        优先级高的星级概率增长时，会挤占优先级低的星级的概率
        星级的概率累加起点及累加值由 star_increase 指定
        由于 StarProbabilityRule 在每次抽卡结束后都将重置概率
        因此本规则只有在先于 StarProbabilityRule 执行时才生效
        """
        for star, (start, increment) in self.star_increase.items():
            counter = ctx.rule_bridge[StarCounterRule.tag].star_counter.get(star, 0) + 1 # type: ignore
            if counter >= start:
                k = counter - start + 1
                ctx.rule_bridge[StarProbabilityRule.tag].star_probability[star] += k * increment # type: ignore
        
        # 对概率进行归一化处理，确保概率权重和为 MAX_PROBABILITY
        total = 0
        for star, probability in ctx.rule_bridge[StarProbabilityRule.tag].star_probability.items(): # type: ignore
            p = max(min(MAX_PROBABILITY - total, probability), 0)
            total += p
            ctx.rule_bridge[StarProbabilityRule.tag].star_probability[star] = p # type: ignore
    
    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        pass

    def load_state(self, state: Dict):
        pass

    def reg_state(self, state: Dict):
        pass


class StarProbabilityIntervalIncreaseRule(BaseRule):
    """
    星级概率区间增长规则
    在 StarProbabilityRule 的基础上, 实现星级概率在不同区间内随抽数内等差增长的规则
    *仅当本规则先于 StarProbabilityRule 执行时生效
    """
    tag: str = "StarProbabilityIntervalIncreaseRule"

    def __init__(self, star_increase: Dict[str, List[Tuple[int, int]]], **kwargs) -> None:
        # 星级 -> (起始抽数, 增长值) 列表
        self.star_increase: Dict[int, List[Tuple[int, int]]] = {
            int(star): [
                    (start, increment) 
                    for start, increment in intervals
                ]
            for star, intervals in star_increase.items()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        修改 StarProbabilityRule 的概率权重，实现概率增长
        每个区间的起始概率都是上个区间的结束概率
        第一个区间的起始概率为 StarProbabilityRule 的基础概率
        """
        # 修改概率权重
        for star, intervals in self.star_increase.items():
            counter = ctx.rule_bridge[StarCounterRule.tag].star_counter.get(star, 0) + 1 # type: ignore
            for start, increment in intervals:
                if counter >= start:
                    k = counter - start + 1
                    ctx.rule_bridge[StarProbabilityRule.tag].star_probability[star] += k * increment # type: ignore
                else:
                    break
        
        # 对概率进行归一化处理，确保概率权重和为 MAX_PROBABILITY
        total = 0
        for star, probability in ctx.rule_bridge[StarProbabilityRule.tag].star_probability.items(): # type: ignore
            p = max(min(MAX_PROBABILITY - total, probability), 0)
            total += p
            ctx.rule_bridge[StarProbabilityRule.tag].star_probability[star] = p # type: ignore

    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        pass

    def load_state(self, state: Dict):
        pass

    def reg_state(self, state: Dict):
        pass


class FesRule(BaseRule):
    """
    Fes 规则
    在 UP 内部进行二次概率提升的规则

    来源: 蔚蓝档案-Fes机制
    """
    tag: str = "FesRule"

    def __init__(self, fes_probability: Dict[str, int], **kwargs):
        self.fes_probability: Dict[int, int] = {
            int(star): probability
            for star, probability in fes_probability.items()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        if ctx.result is None or TAG_UP not in ctx.result.tags or ctx.result.star not in self.fes_probability:
            return
        
        fes_weight = self.fes_probability[ctx.result.star]
        if random.choices((True, False), (fes_weight, MAX_PROBABILITY - fes_weight))[0]:
            ctx.result.tags.append(TAG_FES)

    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        pass

    def load_state(self, state: Dict):
        pass

    def reg_state(self, state: Dict):
        pass


class AppointRule(BaseRule):
    """
    Appoint 规则 (定轨规则)
    在 UP 内部再次指定 Appoint 卡片，当结果为 UP 且计数器超过 Appoint 阈值时，强制结果为 Appoint 卡片的规则
    *Appoint 卡片同时也是 UP 卡片
    *仅当本规则后于 UpRule 执行时生效

    来源: 原神-武器卡池-定轨机制
    """
    tag: str = "AppointRule"

    def __init__(self, appoint_pity: Dict[str, int], **kwargs):
        self.appoint_pity: Dict[int, int] = {
            int(star): pity
            for star, pity in appoint_pity.items()
        }
        self.appoint_counter: Dict[int, int] = {
            star: 0 
            for star in self.appoint_pity.keys()
        }
        self.is_appoint_pity: Dict[int, bool] = {
            star: False 
            for star in self.appoint_pity.keys()
        }
    
    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self
    
    def apply(self, ctx: RuleContext):
        """
        在本抽为 UP 的前提下，检查是否达到 Appoint 阈值，若达到，则强制结果为 Appoint 卡片
        """
        for star in self.appoint_pity.keys():
            self.is_appoint_pity[star] = False

        if ctx.result is None or TAG_UP not in ctx.result.tags:
            return

        star = ctx.result.star
        if star not in self.appoint_pity:
            return
        
        if self.appoint_counter[star] >= self.appoint_pity[star]:
            ctx.result.tags.append(TAG_APPOINT)
            self.appoint_counter[star] = 0
            self.is_appoint_pity[star] = True
            return

        self.appoint_counter[star] += 1

    def callback(self, ctx: RuleContext):
        """
        检查本抽的卡片是否属于 Appoint 组，如果是，则重置 Appoint 计数器
        """
        if ctx.packed_card_result is None or TAG_APPOINT not in ctx.packed_card_result.tags:
            return

        star = ctx.packed_card_result.card.star
        if star not in self.appoint_pity:
            return

        self.appoint_counter[star] = 0

    def reset(self, ctx: RuleContext):
        """
        重置 appoint_counter 计数器和 is_appoint_pity 标记
        """
        self.appoint_counter = {
            star: 0 
            for star in self.appoint_pity.keys()
        }
        self.is_appoint_pity = {
            star: False 
            for star in self.appoint_pity.keys()
        }
    
    def load_state(self, state: Dict):
        """
        加载 appoint_counter 计数器和 is_appoint_pity 保底状态
        """
        if self.tag not in state:
            return
        
        appoint_counter_state = state[self.tag].get("appoint_counter", {})
        for star in self.appoint_pity.keys():
            self.appoint_counter[star] = appoint_counter_state.get(str(star), self.appoint_counter[star])
        
        is_appoint_pity_state = state[self.tag].get("is_appoint_pity", {})
        for star in self.appoint_pity.keys():
            self.is_appoint_pity[star] = is_appoint_pity_state.get(str(star), self.is_appoint_pity[star])

    def reg_state(self, state: Dict):
        """
        注册 appoint_counter 计数器和 is_appoint_pity 保底状态
        """
        appoint_counter_state = {
            str(star): counter 
            for star, counter in self.appoint_counter.items()
        }
        is_appoint_pity_state = {
            str(star): is_appoint_pity
            for star, is_appoint_pity in self.is_appoint_pity.items()
        }

        if appoint_counter_state or is_appoint_pity_state:
            state[self.tag] = {}

            if appoint_counter_state:
                state[self.tag]["appoint_counter"] = appoint_counter_state

            if is_appoint_pity_state:
                state[self.tag]["is_appoint_pity"] = is_appoint_pity_state


class CaptureRule(BaseRule):
    """
    Capture 规则 (捕获规则)
    在进行 UP 抽取前，优先进行捕获判定, 若判定成功, 则直接判定为 UP
    *仅当本规则先于 UpRule 执行时生效

    来源: 原神-武器卡池-捕获明光机制
    """
    tag: str = "CaptureRule"

    def __init__(self, capture_probability: Dict[str, int], **kwargs):
        self.capture_probability: Dict[int, int] = {
            int(star): probability
            for star, probability in capture_probability.items()
        }

    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        捕获判定
        """
        if ctx.result is None:
            return
        
        if TAG_UP in ctx.result.tags:
            return

        star = ctx.result.star
        if star not in self.capture_probability:
            return

        if random.choices((True, False), (self.capture_probability[star], MAX_PROBABILITY - self.capture_probability[star]))[0]:
            ctx.result.tags.append(TAG_UP)

    def callback(self, ctx: RuleContext):
        pass

    def reset(self, ctx: RuleContext):
        pass

    def load_state(self, state: Dict):
        pass

    def reg_state(self, state: Dict):
        pass


class CapturePityRule(BaseRule):
    """
    CapturePity 规则 (捕获保底规则)
    若连续 n 次通过 UP 保底才获取 UP, 则下次获取该星级时, 必定触发捕获机制
    *仅当本规则先于 UpRule 执行时生效

    来源: 原神-武器卡池-捕获明光机制:
    若连续三次在第二次获取5星角色时才获取本期5星UP角色，下次祈愿获取5星角色时，必定触发「捕获明光」机制。
    """
    tag: str = "CapturePityRule"

    def __init__(self, capture_pity: Dict[str, int], **kwargs):
        self.capture_pity: Dict[int, int] = {
            int(star): pity
            for star, pity in capture_pity.items()
        }
        self.capture_pity_counter = {
            star: 0 
            for star in self.capture_pity.keys()
        }
        self.is_capture_pity = {
            star: False 
            for star in self.capture_pity.keys()
        }

    def set_bridge(self, ctx: RuleContext):
        ctx.rule_bridge[self.tag] = self

    def apply(self, ctx: RuleContext):
        """
        捕获保底判定
        """
        for star in self.capture_pity.keys():
            self.is_capture_pity[star] = False

        if ctx.result is None:
            return
        
        star = ctx.result.star

        if star not in self.capture_pity:
            return
        
        if self.capture_pity_counter[star] >= self.capture_pity[star]:
            ctx.result.tags.append(TAG_UP)
            self.is_capture_pity[star] = True
            self.capture_pity_counter[star] = 0
            return

        # if TAG_UP in ctx.result.tags:
        #     self.capture_pity_counter[star] = 0     # 触发 UP, 重置计数器
        #     return

        # star = ctx.result.star
        # if star not in self.capture_pity:
        #     return

        # if self.capture_pity_counter[star] >= self.capture_pity[star]:
        #     ctx.result.tags.append(TAG_UP)
        #     self.is_capture_pity[star] = True
        #     self.capture_pity_counter[star] = 0
        #     return

        # # 更新捕获保底计数器
        # if TAG_UP not in ctx.result.tags:
        #     self.capture_pity_counter[star] += 1
        
        # if UpRule.tag not in ctx.rule_bridge:
        #     return
        
        # up_rule = ctx.rule_bridge[UpRule.tag]
        # if star not in up_rule.up_pity: # type: ignore
        #     return

        # if up_rule.is_up_pity[star]: # type: ignore
        #     self.capture_pity_counter[star] += 1

    def callback(self, ctx: RuleContext):
        """
        更新 capture_pity_counter 捕获保底计数器
        """
        if ctx.result is None:
            return

        star = ctx.result.star

        if star not in self.capture_pity:
            return

        if UpRule.tag not in ctx.rule_bridge:
            return
        
        up_rule = ctx.rule_bridge[UpRule.tag]
        if star not in up_rule.up_pity: # type: ignore
            return

        if up_rule.is_up_pity[star] and TAG_UP in ctx.result.tags: # type: ignore
            self.capture_pity_counter[star] += 1
            return
        
        if TAG_UP in ctx.result.tags:
            self.capture_pity_counter[star] = 0

    def reset(self, ctx: RuleContext):
        """
        重置 capture_pity_counter 捕获保底计数器和 is_capture_pity 保底状态
        """
        self.capture_pity_counter = {
            star: 0 
            for star in self.capture_pity.keys()
        }
        self.is_capture_pity = {
            star: False 
            for star in self.capture_pity.keys()
        }

    def load_state(self, state: Dict):
        """
        加载 capture_pity_counter 捕获保底计数器和 is_capture_pity 保底状态
        """
        if self.tag not in state:
            return

        capture_pity_counter_state = state[self.tag].get("capture_pity_counter", {})

        for star in self.capture_pity.keys():
            self.capture_pity_counter[star] = capture_pity_counter_state.get(str(star), self.capture_pity_counter[star])
        
        is_capture_pity_state = state[self.tag].get("is_capture_pity", {})
        for star in self.capture_pity.keys():
            self.is_capture_pity[star] = is_capture_pity_state.get(str(star), self.is_capture_pity[star])

    def reg_state(self, state: Dict):
        """
        注册 capture_pity_counter 捕获保底计数器和 is_capture_pity 保底状态
        """
        capture_pity_counter_state = {
            str(star): counter
            for star, counter in self.capture_pity_counter.items()
        }

        is_capture_pity_state = {
            str(star): is_capture
            for star, is_capture in self.is_capture_pity.items()
        }

        if capture_pity_counter_state or is_capture_pity_state:
            state[self.tag] = {}

            if capture_pity_counter_state:
                state[self.tag]["capture_pity_counter"] = capture_pity_counter_state

            if is_capture_pity_state:
                state[self.tag]["is_capture_pity"] = is_capture_pity_state


class WishLogic:
    """
    核心逻辑驱动引擎
    """
    def __init__(self, config: Dict) -> None:
        """
        config 结构:
        config: {
            "name": str,
            "rules": {
                "tag": {
                    "param": value,
                    ...
                },
                ...
            }
        }
        """
        self.name = config["name"] if "name" in config else ""

        rule_config: Dict[str, Dict] = config["rules"]
        self.rules: List[BaseRule] = [
            tag_to_rule_class(rule_class_tag)(**rule_class_config)
            for rule_class_tag, rule_class_config in rule_config.items()
        ]

        self.ctx = RuleContext()
        for rule in self.rules:
            rule.set_bridge(self.ctx)

    def wish(self) -> LogicResult:
        """
        抽卡
        """
        self.ctx.result = None
        self.ctx.packed_card_result = None

        for rule in self.rules:
            rule.apply(self.ctx)        # 逐级执行规则，确定抽卡结果

        result = self.ctx.result if self.ctx.result else LogicResult(star=0, type_="")

        return result

    def callback(self, packed_card: PackedCard):
        """
        抽卡结束，回调逻辑
        """
        self.ctx.packed_card_result = packed_card

        for rule in self.rules:
            rule.callback(self.ctx)

    def reset(self):
        """
        逻辑状态重置
        """
        self.ctx.result = None

        for rule in self.rules:
            rule.reset(self.ctx)

    def load_state(self, state: Dict):
        """
        加载逻辑状态
        """
        for rule in self.rules:
            rule.load_state(state)

    def reg_state(self, state: Dict):
        """
        注册逻辑状态
        """
        for rule in self.rules:
            rule.reg_state(state)

    def copy(self) -> "WishLogic":
        """
        创建深拷贝副本
        """
        logic = deepcopy(self)

        return logic

    @staticmethod
    def none() -> "WishLogic":
        """
        创建空逻辑
        """
        return WishLogic({
            "name": "None",
            "rules": {}
        })


def tag_to_rule_class(rule_tag: str) -> Type[BaseRule]:
    match rule_tag:
        case StarCounterRule.tag:
            return StarCounterRule
        case TypeStarCounterRule.tag:
            return TypeStarCounterRule
        case StarProbabilityRule.tag:
            return StarProbabilityRule
        case TypeStarProbabilityRule.tag:
            return TypeStarProbabilityRule
        case StarPityRule.tag:
            return StarPityRule
        case TypeStarPityRule.tag:
            return TypeStarPityRule
        case UpRule.tag:
            return UpRule
        case UpTypeRule.tag:
            return UpTypeRule
        case StarProbabilityIncreaseRule.tag:
            return StarProbabilityIncreaseRule
        case StarProbabilityIntervalIncreaseRule.tag:
            return StarProbabilityIntervalIncreaseRule
        case FesRule.tag:
            return FesRule
        case AppointRule.tag:
            return AppointRule
        case CaptureRule.tag:
            return CaptureRule
        case CapturePityRule.tag:
            return CapturePityRule
        case _:
            return BaseRule


if __name__ == "__main__":
    pass
    # 测试
    # config = {
    #     "rules": [
    #         StarPityRule,
    #         StarProbabilityIncreaseRule,
    #         StarProbabilityRule,
    #         UpRule,
    #         UpTypeRule,
    #         TypeStarPityRule,
    #         TypeStarProbabilityRule,
    #         StarCounterRule,
    #         TypeStarCounterRule
    #     ],
    #     "star_probability": {
    #         5: 60,
    #         4: 510,
    #         3: 9430
    #     },
    #     "type_probability": {
    #         5: {"Role": 10000},
    #         4: {"Role": 5000, "Weapon": 5000},
    #         3: {"Weapon": 10000}
    #     },
    #     "star_pity": {
    #         5: 90,
    #         4: 10
    #     },
    #     "type_pity": {
    #         4: {"Role": 1}
    #     },
    #     "up_probability": {
    #         5: 5000,
    #         4: 5000
    #     },
    #     "up_pity": {
    #         5: 1,
    #         4: 1
    #     },
    #     "up_type_probability": {
    #         5: {"Role": 10000},
    #         4: {"Role": 10000}
    #     },
    #     "up_type_pity": {
    #         5: {"Role": 1},
    #         4: {"Role": 1}
    #     },
    #     "star_increase": {
    #         5: (73, 600),
    #         4: (9, 5100)
    #     }
    # }
    # logic = WishLogic(config)
    # counter = 0
    # while True:
    #     counter += 1
    #     input()
    #     res = logic.wish()
    #     print(f"{counter}. {res}")
    #     print(logic.ctx.parameters[StarProbabilityRule.tag])
    #     if res.star == 5:
    #         counter = 0
    #         print("-" * 40)
