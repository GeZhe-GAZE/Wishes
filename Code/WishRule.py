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
import random


class RuleContext:
    """
    规则执行上下文
    """
    def __init__(self) -> None:
        # 当前抽结果
        self.result: Optional[LogicResult] = None
        # 规则参数表，由规则自行管理自身参数，提供对其他规则的参数访问
        self.parameters: Dict[str, Dict] = {}


class BaseRule(ABC):
    """
    规则基类
    """
    # 规则标识符
    tag: str = "BaseRule"

    def __init__(self, **kwargs):
        super().__init__()
    
    @abstractmethod
    def set_parameters(self, ctx: RuleContext):
        """
        初始化时，在上下文中注册属性
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


class StarCounterRule(BaseRule):
    """
    星级计数器规则
    提供每个星级的抽卡计数，计数器会在抽出对应星级后重置
    所有操作在回调函数中完成
    """
    tag: str = "StarCounterRule"

    def __init__(self, star_probability: Dict[int, int] ,**kwargs):
        """
        星级计数器初始化为 0
        由于计数器在回调过程中更新
        因此，当前实际抽数是 计数器值 + 1
        故各类型在使用本规则的计数器时需自加 1
        """
        self.counter = {star: 0 for star in star_probability.keys()}

    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "counter": self.counter
        }

    def apply(self, ctx: RuleContext):
        """
        不操作
        """
        # for star in self.counter.keys():
        #     self.counter[star] += 1
        
        # if ctx.result and ctx.result.star:
        #     self.counter[ctx.result.star] = 0
    
    def callback(self, ctx: RuleContext):
        """
        回调中，更新星级计数器
        """
        for star in self.counter.keys():
            self.counter[star] += 1
        
        if ctx.result and ctx.result.star:
            self.counter[ctx.result.star] = 0


class TypeStarCounterRule(BaseRule):
    """
    基于星级的类型计数器规则
    提供每个星级下各类型的抽卡计数，计数器会在抽出对应类型后重置
    所有操作在回调函数中完成
    """
    tag: str = "TypeStarCounterRule"

    def __init__(self, type_probability: Dict[int, Dict[str, int]], **kwargs):
        self.counter = {
            star: {type_: 0 for type_ in type_probability[star].keys()} 
            for star in type_probability.keys()
        }
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "counter": self.counter
        }
    
    def apply(self, ctx: RuleContext):
        """
        不操作
        """
        # if ctx.result and ctx.result.star in self.counter:
        #     for type_ in self.counter[ctx.result.star].keys():
        #         if type_ == ctx.result.type_:
        #             self.counter[ctx.result.star][type_] = 0
        #             continue
        #         self.counter[ctx.result.star][type_] += 1

        # for star in self.counter.keys():
        #     for type_ in self.counter[star].keys():
        #         self.counter[star][type_] += 1
        
        # if ctx.result and \
        #    ctx.result.star in self.counter and \
        #    ctx.result.type_ in self.counter[ctx.result.star]:
        #     self.counter[ctx.result.star][ctx.result.type_] = 0
    
    def callback(self, ctx: RuleContext):
        """
        回调中，更新类型计数器
        """
        if ctx.result and ctx.result.star in self.counter:
            for type_ in self.counter[ctx.result.star].keys():
                if type_ == ctx.result.type_:
                    self.counter[ctx.result.star][type_] = 0
                    continue
                self.counter[ctx.result.star][type_] += 1


class StarProbabilityRule(BaseRule):
    """
    星级基础概率规则
    根据当前星级概率权重决定当前抽星级
    每次回调都会重置概率为基础概率
    """
    tag: str = "StarProbabilityRule"

    def __init__(self, star_probability: Dict[int, int], **kwargs):
        self.star_probability = star_probability
        self.base_probability = self.star_probability.copy()
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "star_probability": self.star_probability,
            "base_probability": self.base_probability
        }

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
        ctx.parameters[self.tag]["star_probability"] = self.star_probability


class TypeStarProbabilityRule(BaseRule):
    """
    基于星级的类型基础概率规则
    根据当前星级，和星级对应的类型概率权重决定当前抽类型
    """
    tag: str = "TypeStarProbabilityRule"

    def __init__(self, type_probability: Dict[int, Dict[str, int]], **kwargs):
        self.type_probability = type_probability
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "type_probability": self.type_probability
        }

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


class StarPityRule(BaseRule):
    """
    星级保底规则
    提供对应星级的保底，若抽卡次数达到阈值，则触发保底，并重置计数器
    *不同星级的保底触发优先级遵循 star_pity 中设定的星级顺序
    """
    tag: str = "StarPityRule"

    def __init__(self, star_pity: Dict[int, int], **kwargs) -> None:
        self.star_pity = star_pity
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "star_pity": self.star_pity
        }
    
    def apply(self, ctx: RuleContext):
        """
        检查星级保底，若触发，则按 star_pity 字典中顺序取最先触发保底星级
        若星级保底被更大的星级保底覆盖，则不会重置保底
        本规则决定的星级优先级大于 StarProbabilityRule
        """
        star_counter = ctx.parameters[StarCounterRule.tag]["counter"]
        for star, threshold in self.star_pity.items():
            counter = star_counter.get(star, 0) + 1
            if counter >= threshold:
                ctx.result = LogicResult(star=star, type_="")
                star_counter[star] = 0
                return
    
    def callback(self, ctx: RuleContext):
        pass


class TypeStarPityRule(BaseRule):
    """
    基于星级的类型保底规则
    提供对应星级的类型保底，若抽卡次数达到阈值，则触发保底，并重置计数器
    *不同类型的保底触发优先级遵循 type_pity 中该星级下设定的类型顺序
    """
    tag: str = "TypeStarPityRule"

    def __init__(self, type_pity: Dict[int, Dict[str, int]], **kwargs) -> None:
        self.type_pity = type_pity
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "type_pity": self.type_pity
        }

    def apply(self, ctx: RuleContext):
        """
        根据星级，获取对应的类型保底
        检查该星级各类型保底，若触发，则按 type_pity 字典中顺序取最先触发保底的类型
        若类型已被决定，则将重置该类型保底，且不操作
        本规则决定的类型优先级大于 TypeStarProbabilityRule
        """
        if ctx.result is None or not ctx.result.star:
            return

        type_counter = ctx.parameters[TypeStarCounterRule.tag]["counter"]
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
                return
    
    def callback(self, ctx: RuleContext):
        pass


class UpRule(BaseRule):
    """
    UP 规则
    将 UP 卡片设定为拥有显著高于同星级基础概率的抽取出现率的规则
    同时附带对 UP 卡片的计数器和保底机制
    """
    tag: str = "UpRule"

    def __init__(self, up_probability: Dict[int, int], up_pity: Dict[int, int] ,**kwargs) -> None:
        self.up_probability = up_probability
        self.up_pity = up_pity
        self.up_counter: Dict[int, int] = {
            star: 0
            for star in self.up_probability.keys()
        }
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "up_probability": self.up_probability,
            "up_pity": self.up_pity,
            "up_counter": self.up_counter
        }
    
    def apply(self, ctx: RuleContext):
        """
        根据星级，获取对应的 UP 保底
        若触发保底则决定为 UP
        若未触发，则根据 up_probability 中指定的对应星级的 UP 概率权重决定是否 UP
        """
        if ctx.result is None or ctx.result.star not in self.up_probability:
            return
        
        counter = self.up_counter[ctx.result.star]
        if ctx.result.star in self.up_pity and counter >= self.up_pity[ctx.result.star]:
            ctx.result.tag = TAG_UP
            self.up_counter[ctx.result.star] = 0
        else:
            self.up_counter[ctx.result.star] += 1

            up_weight = self.up_probability[ctx.result.star]
            ctx.result.tag = random.choices((TAG_UP, TAG_RESIDENT), (up_weight, MAX_PROBABILITY - up_weight))[0]
    
    def callback(self, ctx: RuleContext):
        pass


class UpTypeRule(BaseRule):
    """
    UP 类型分布规则
    在同星级的 UP 卡片内部，支持设定不同类型的 UP 卡片概率权重的规则
    同时附带基于星级的对 UP 类型的计数器和保底机制
    """
    tag: str = "UpTypeRule"

    def __init__(self, up_type_probability: Dict[int, Dict[str, int]], up_type_pity: Dict[int, Dict[str, int]], **kwargs):
        self.up_type_probability = up_type_probability
        self.up_type_pity = up_type_pity
        self.up_type_counter = {
            star: {type_: 0 for type_ in self.up_type_probability[star].keys()}
            for star in self.up_type_probability.keys()
        }
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "up_type_probability": self.up_type_probability,
            "up_type_pity": self.up_type_pity,
            "up_type_counter": self.up_type_counter
        }
    
    def apply(self, ctx: RuleContext):
        """
        在当前为 UP 的情况下，根据概率权重决定类型
        所有可 UP 类型及对应权重由 up_type_probability 指定
        """
        if ctx.result is None or ctx.result.star not in self.up_type_probability or ctx.result.tag != TAG_UP:
            return
        
        counter = self.up_type_counter[ctx.result.star]
        for type_ in counter.keys():
            counter[type_] += 1
        for type_ in counter.keys():
            if counter[type_] >= self.up_type_pity[ctx.result.star][type_]:
                ctx.result.type_ = type_
                return
        
        types = tuple(self.up_type_probability[ctx.result.star].keys())
        weights = tuple(self.up_type_probability[ctx.result.star].values())
        ctx.result.type_ = random.choices(types, weights=weights)[0]
    
    def callback(self, ctx: RuleContext):
        pass


class StarProbabilityIncreaseRule(BaseRule):
    """
    星级概率增长规则
    在 StarProbabilityRule 的基础上，实现不同星级概率随抽数增加而等差增长的规则
    *仅当本规则先于 StarProbabilityRule 执行时生效
    """
    tag: str = "StarProbabilityIncreaseRule"

    def __init__(self, star_increase: Dict[int, Tuple[int, int]],**kwargs) -> None:
        self.star_increase = star_increase
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "star_increase": self.star_increase
        }
    
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
            counter = ctx.parameters[StarCounterRule.tag]["counter"].get(star, 0) + 1
            if counter >= start:
                k = counter - start + 1
                ctx.parameters[StarProbabilityRule.tag]["star_probability"][star] += k * increment
        
        # 对概率进行归一化处理，确保概率权重和为 MAX_PROBABILITY
        total = 0
        for star, probability in ctx.parameters[StarProbabilityRule.tag]["star_probability"].items():
            p = max(min(MAX_PROBABILITY - total, probability), 0)
            total += p
            ctx.parameters[StarProbabilityRule.tag]["star_probability"][star] = p
    
    def callback(self, ctx: RuleContext):
        pass


class FesRule(BaseRule):
    """
    Fes 规则
    在 UP 内部进行二次概率提升的规则
    """
    tag: str = "FesRule"

    def __init__(self, fes_probability: Dict[int, int], **kwargs):
        self.fes_probability = fes_probability
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "fes_probability": self.fes_probability
        }
    
    def apply(self, ctx: RuleContext):
        if ctx.result is None or ctx.result.tag != TAG_UP or ctx.result.star not in self.fes_probability:
            return
        
        fes_weight = self.fes_probability[ctx.result.star]
        print(fes_weight, MAX_PROBABILITY - fes_weight)
        ctx.result.tag = random.choices((TAG_FES, TAG_UP), (fes_weight, MAX_PROBABILITY - fes_weight))[0]

    def callback(self, ctx: RuleContext):
        pass


class AppointRule(BaseRule):
    """
    Appoint 规则 (定轨规则)
    在 UP 内部再次指定 Appoint 卡片，当结果为 UP 且计数器超过 Appoint 阈值时，强制结果为 Appoint 卡片的规则
    *Appoint 卡片同时也是 UP 卡片
    *仅当本规则后于 UpRule 执行时生效
    """
    tag: str = "AppointRule"

    def __init__(self, appoint_pity: Dict[int, int], **kwargs):
        self.appoint_pity = appoint_pity
        self.appoint_counter = {
            star: 0 
            for star in self.appoint_pity.keys()
        }
    
    def set_parameters(self, ctx: RuleContext):
        ctx.parameters[self.tag] = {
            "appoint_pity": self.appoint_pity,
            "appoint_counter": self.appoint_counter
        }
    
    def apply(self, ctx: RuleContext):
        if ctx.result is None or ctx.result.tag not in (TAG_UP, TAG_FES):
            return

        star = ctx.result.star
        if star not in self.appoint_pity:
            return
        
        if self.appoint_counter[star] >= self.appoint_pity[star]:
            ctx.result.tag = TAG_APPOINT
            self.appoint_counter[star] = 0
            return

        self.appoint_counter[star] += 1

    def callback(self, ctx: RuleContext):
        pass


class WishLogic:
    """
    核心逻辑驱动引擎
    """
    def __init__(self, config: Dict) -> None:
        self.name = config["name"] if "name" in config else ""
        self.rules: List[BaseRule] = [rule_class(**config) for rule_class in config["rules"]]

        self.ctx = RuleContext()
        for rule in self.rules:
            rule.set_parameters(self.ctx)
    
    def wish(self) -> LogicResult:
        self.ctx.result = None

        for rule in self.rules:
            rule.apply(self.ctx)        # 逐级执行规则，确定抽卡结果

        result = self.ctx.result if self.ctx.result else LogicResult(star=0, type_="")

        for rule in self.rules:
            rule.callback(self.ctx)     # 逐级回调，执行计数器更新等其他操作

        return result


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
        case FesRule.tag:
            return FesRule
        case AppointRule.tag:
            return AppointRule
        case _:
            return BaseRule

if __name__ == "__main__":
    # 测试
    config = {
        "rules": [
            StarPityRule,
            StarProbabilityIncreaseRule,
            StarProbabilityRule,
            UpRule,
            UpTypeRule,
            TypeStarPityRule,
            TypeStarProbabilityRule,
            StarCounterRule,
            TypeStarCounterRule
        ],
        "star_probability": {
            5: 60,
            4: 510,
            3: 9430
        },
        "type_probability": {
            5: {"Role": 10000},
            4: {"Role": 5000, "Weapon": 5000},
            3: {"Weapon": 10000}
        },
        "star_pity": {
            5: 90,
            4: 10
        },
        "type_pity": {
            4: {"Role": 1}
        },
        "up_probability": {
            5: 5000,
            4: 5000
        },
        "up_pity": {
            5: 1,
            4: 1
        },
        "up_type_probability": {
            5: {"Role": 10000},
            4: {"Role": 10000}
        },
        "up_type_pity": {
            5: {"Role": 1},
            4: {"Role": 1}
        },
        "star_increase": {
            5: (73, 600),
            4: (9, 5100)
        }
    }
    logic = WishLogic(config)
    counter = 0
    while True:
        counter += 1
        input()
        res = logic.wish()
        print(f"{counter}. {res}")
        print(logic.ctx.parameters[StarProbabilityRule.tag])
        if res.star == 5:
            counter = 0
            print("-" * 40)
