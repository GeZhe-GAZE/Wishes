r"""
Wishes v3.0
-----------

Module
_
    Base

Description
_
    Wishes 基础类型定义
    受其他模块依赖
"""


import json
import os
from random import choice
from Const import *
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class Card:
    """
    卡片类，封装卡片的各种属性
    每个卡片都是全局单例
    """
    content: str            # 卡片内容
    game: str               # 卡片所属游戏
    star: int               # 卡片星级
    type: str               # 卡片类型  角色/武器
    attribute: str          # 卡片属性  冰/火/...
    title: str = ""         # 卡片称号，用于抽卡界面显示
    profession: str = ""    # 卡片职业类型  智识/单手剑/击破
    image_path: str = ""    # 图片路径
    
    def __str__(self) -> str:
        return f"Card({self.content}, {self.star}, {self.type}, {self.attribute}, {self.profession}, {self.image_path})"
    
    @staticmethod
    def load_from_json(file: str) -> "Card":
        """
        从 json 文件中加载
        """
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Card(
            content=data["content"],
            game=data["game"],
            star=data["star"],
            type=data["type"],
            attribute=data["attribute"],
            title=data["title"],
            profession=data["profession"],
            image_path=data["image_path"]
        )

    @staticmethod
    def none() -> "Card":
        """
        返回空卡片
        """
        return Card(content="", game="", star=0, type="", attribute="")
    
    def usable(self) -> bool:
        """
        判断卡片是否可用
        """
        return self.content != "" and \
               self.game != "" and \
               self.star != 0 and \
               self.type != ""


class PackedCard:
    """
    对卡片的二次封装，用于在抽卡时使用
    """
    def __init__(self, card: Card, real_tag: str = TAG_RESIDENT, tags: List[str] = [TAG_RESIDENT], rarity: str = ""):
        self.card = card            # 卡片对象
        self.real_tag = real_tag    # 卡片被抽出时，所属的标签组
        self.tags = tags            # 卡片所属的所有标签组
        self.rarity = rarity        # 卡片稀有度映射

    def __str__(self) -> str:
        return f"PackedCard({self.card}, {self.real_tag}, {self.tags}, {self.rarity})"


class SingleTagCardGroup:
    """
    单标签卡池组
    处理单个标签组内的卡片管理
    管理结构：
    类型 -> 星级 -> 卡片名称: 卡片对象
    """
    def __init__(self, name: str):
        self.name = name

        # 类型 -> 星级 -> 卡片名称: 卡片对象
        self.cards: Dict[str, Dict[int, Dict[str, Card]]] = {}
        # 卡片总数
        self.count = 0
        # 最高星级 (最高稀有度)
        self.max_star = 0

        # 排除的卡片，抽卡将不抽出这些卡片，同时也不视为存在于卡组中
        self.exclude_cards: Dict[str, Dict[int, List[str]]] = {}
    
    def __str__(self) -> str:
        cards_info = "\n".join([
            f"  - {type_}:\n" + "\n".join([
                f"    - Star{star}:\n" + "\n".join([
                    f"      - {card}"
                    for card in card_dict.values()
                ])
                for star, card_dict in star_dict.items()
            ])
            for type_, star_dict in self.cards.items()
        ])

        exclude_info = "- *exclude_cards:\n" + "\n".join([
            f"  - {type_}:\n" + "\n".join([
                f"    - Star{star}:\n" + "\n".join([
                    f"      - {card}"
                    for card in card_list
                ])
                for star, card_list in star_dict.items()
            ])
            for type_, star_dict in self.exclude_cards.items()
        ])

        return "\n".join([
            f"SingleTagCardGroup <{self.name}>",
            f"- count: {self.count}",
            f"- max_star: {self.max_star}",
            "- cards:",
            cards_info,
            exclude_info if self.exclude_cards else "",
        ])
    
    def add_type(self, type_: str):
        """
        添加卡片类型
        """
        if type_ not in self.cards:
            self.cards[type_] = {}
    
    def add_star(self, type_: str, star: int):
        """
        添加星级
        """
        if type_ not in self.cards:
            self.cards[type_] = {}
        if star not in self.cards[type_]:
            self.cards[type_][star] = {}
    
    def add_card(self, card: Card):
        """
        添加卡片
        """
        if card.type not in self.cards:
            self.cards[card.type] = {}
        if card.star not in self.cards[card.type]:
            self.cards[card.type][card.star] = {}

        target = self.cards[card.type][card.star]
        if card.content not in target:
            target[card.content] = card
            self.count += 1
            self.max_star = max(self.max_star, card.star)
    
    def add_exclude_card(self, card: Card):
        """
        添加排除卡片
        """
        if card.type not in self.exclude_cards:
            self.exclude_cards[card.type] = {}
        
        if card.star not in self.exclude_cards[card.type]:
            self.exclude_cards[card.type][card.star] = []

        self.exclude_cards[card.type][card.star].append(card.content)
    
    def has_exclude_card(self, card: Card) -> bool:
        """
        判断卡片是否被排除
        """
        return card.content in self.exclude_cards.get(card.type, {}).get(card.star, [])
    
    def clear_exclude_card(self):
        """
        清空排除卡片
        """
        self.exclude_cards = {}
    
    def random_card(self, type_: str, star: int) -> Card:
        """
        随机抽取一个卡片
        """
        if type_ not in self.cards or star not in self.cards[type_]:
            return Card.none()

        target = self.cards[type_][star]

        if self.exclude_cards and type_ in self.exclude_cards and star in self.exclude_cards[type_]:
            target = {k: v for k, v in target.items() if k not in self.exclude_cards[type_][star]}

        if not target:
            return Card.none()

        return choice(list(target.values()))
    
    def remove_card(self, type_: str, star: int, content: str):
        """
        删除卡片
        """
        target = self.cards[type_][star]
        if content in target:
            del target[content]
            self.count -= 1
            if star >= self.max_star:
                # 更新最高星级
                self.max_star = max([max(stars.keys()) for stars in self.cards.values()])
    
    def types(self) -> List[str]:
        """
        获取所有类型
        """
        return list(self.cards.keys())
    
    def stars(self, type_: str) -> List[int]:
        """
        获取指定类型组内所有星级
        """
        if type_ not in self.cards:
            return []
        return list(self.cards[type_].keys())
    
    def card_contents(self, type_: str, star: int) -> List[str]:
        """
        获取指定类型组内指定星级内所有卡片名称
        """
        if type_ not in self.cards or star not in self.cards[type_]:
            return []
        return list(self.cards[type_][star].keys())

    def all_cards(self) -> List[Card]:
        """
        获取所有卡片
        """
        return [card for stars in self.cards.values() for card_dict in stars.values() for card in card_dict.values()]

class CardGroup:
    """
    完整卡组类
    卡池管理结构：
    标签 -> 类型 -> 星级 -> 卡片名称: 卡片对象
    默认带有 TAG_RESIDENT 标签
    可添加 TAG_UP, TAG_FES, TAG_APPOINT 标签

    *在 Wishes 中，所有非 TAG_UP, TAG_FES, TAG_APPOINT 标签的卡片均视为 TAG_RESIDENT 标签组
    """
    def __init__(
            self, 
            name: str, 
            resident_card_group: SingleTagCardGroup | None = None, 
            version: str = "", 
            is_official: bool = False
            ):
        self.name = name                        # 卡组名称
        self.is_official = is_official          # 是否为官方卡组
        self.version = version                  # 卡组版本，仅在官方卡组内可用

        resident_card_group = SingleTagCardGroup(self.name + f"-{TAG_RESIDENT}") if not resident_card_group else resident_card_group
        
        # 卡池管理结构
        self.single_tag_card_groups: Dict[str, SingleTagCardGroup] = {TAG_RESIDENT: resident_card_group}
        # 最高星级 (最高稀有度)
        self.max_star = resident_card_group.max_star
        # 卡片总数
        self.count = resident_card_group.count


    
    def __str__(self) -> str:
        cards_info = "\n".join([
            f"  - {tag} group:\n" + "\n".join(["    " + row for row in str(group).split("\n")])
            for tag, group in self.single_tag_card_groups.items()
        ])

        return "\n".join((
            f"CardGroup <{self.name}> " + "-" * 30,
            f"version: {self.version if self.version else "no-version"} | is_official: {self.is_official}",
            f"- count: {self.count}",
            f"- max_star: {self.max_star}",
            "- cards:",
            cards_info
        ))
    
    def add_tag_group(self, tag: str, card_group: SingleTagCardGroup | None = None):
        """
        添加标签组
        """
        if tag not in self.single_tag_card_groups:
            self.single_tag_card_groups[tag] = SingleTagCardGroup(self.name + f"-{tag}") if not card_group else card_group
            self.max_star = max(self.max_star, self.single_tag_card_groups[tag].max_star)
            self.count += self.single_tag_card_groups[tag].count

    # def add_up(self, up_group: SingleTagCardGroup | None = None):
    #     """
    #     添加 UP 组
    #     """
    #     if TAG_UP not in self.cards:
    #         self.cards[TAG_UP] = SingleTagCardGroup(self.name + f"-{TAG_UP}") if not up_group else up_group
    
    # def add_fes(self, fes_group: SingleTagCardGroup | None = None):
    #     """
    #     添加 Fes 组
    #     """
    #     if TAG_FES not in self.cards:
    #         self.cards[TAG_FES] = SingleTagCardGroup(self.name + f"-{TAG_FES}") if not fes_group else fes_group
    
    # def add_appoint(self, appoint_group: SingleTagCardGroup | None = None):
    #     """
    #     添加 定轨 组
    #     """
    #     if TAG_APPOINT not in self.cards:
    #         self.cards[TAG_APPOINT] = SingleTagCardGroup(self.name + f"-{TAG_APPOINT}") if not appoint_group else appoint_group
    
    def add_type(self, type_: str, tag: str = TAG_RESIDENT):
        """
        在指定组中添加卡片类型
        """
        if tag not in self.single_tag_card_groups:
            return
        if type_ not in self.single_tag_card_groups[tag].types():
            self.single_tag_card_groups[tag].add_type(type_)

    def add_star(self, type_: str, star: int, tag: str = TAG_RESIDENT):
        """
        在指定组的类型组中添加星级
        """
        if tag not in self.single_tag_card_groups:
            return
        if type_ not in self.single_tag_card_groups[tag].types():
            return
        if star not in self.single_tag_card_groups[tag].stars(type_):
            self.single_tag_card_groups[tag].add_star(type_, star)
            self.max_star = max(self.max_star, star)
    
    def add_card(self, card: Card, tag: str = TAG_RESIDENT):
        """
        添加卡片到指定组
        """
        if tag not in self.single_tag_card_groups:
            return
        if card.type not in self.single_tag_card_groups[tag].types():
            return
        if card.star not in self.single_tag_card_groups[tag].stars(card.type):
            return
        
        target = self.single_tag_card_groups[tag].card_contents(card.type, card.star)
        if card.content not in target:
            self.single_tag_card_groups[tag].add_card(card)
            self.count += 1
            self.max_star = max(self.max_star, card.star)

    def random_card(self, type_: str, star: int, tag: str = TAG_RESIDENT) -> PackedCard:
        """
        随机抽取一个卡片
        """
        if tag not in self.single_tag_card_groups or \
              type_ not in self.single_tag_card_groups[tag].types() or \
                  star not in self.single_tag_card_groups[tag].stars(type_):
            return PackedCard(Card.none())
        
        card = self.single_tag_card_groups[tag].random_card(type_, star)

        tags = [tag]

        # 检查卡片是否存在于其他标签组
        for t in self.single_tag_card_groups.keys():
            if t == tag:
                continue
            if card.type not in self.single_tag_card_groups[t].types():
                continue
            if card.star not in self.single_tag_card_groups[t].stars(card.type):
                continue
            if card.content not in self.single_tag_card_groups[t].card_contents(card.type, card.star):
                continue
            if not self.single_tag_card_groups[t].has_exclude_card(card):
                tags.append(t)

        return PackedCard(card, tag, tags)

    def remove_card(self, type_: str, star: int, content: str, tag: str = TAG_RESIDENT):
        """
        删除卡片
        """
        if tag not in self.single_tag_card_groups:
            return
        
        self.count -= self.single_tag_card_groups[tag].count
        self.single_tag_card_groups[tag].remove_card(type_, star, content)   # 删除卡片
        self.count += self.single_tag_card_groups[tag].count     # 通过两次加减卡片数，自动适配卡片删除成功/失败时的卡片数量变化
        # 更新最高星级
        self.max_star = max([group.max_star for group in self.single_tag_card_groups.values()])
    
    def set_exclude(self, usable: bool):
        """
        设置是否启用卡组排除
        将优先卡组中的卡片在次优先卡组中标记为排除卡片 (保证优先卡组中的卡片不会在次优先卡组中抽取到)
        不同标签的卡组优先级如下：
        Fes > UP > Resident
        Appoint 组不参与排除
        """
        if not usable:
            # 取消排除
            for group in self.single_tag_card_groups.values():
                group.clear_exclude_card()
            return
        
        # 定义优先级顺序(从高到低)
        PRIORITY_HIERARCHY = [
            TAG_FES,
            TAG_UP,
            TAG_RESIDENT,
        ]

        # 收集所有需操作的存在卡池
        existing_groups = []
        for tag in PRIORITY_HIERARCHY:
            if tag in self.single_tag_card_groups:
                existing_groups.append(self.single_tag_card_groups[tag])

        # 按优先级顺序进行排除操作
        for i, higher_group in enumerate(existing_groups):
            for lower_group in existing_groups[i + 1:]:
                for card in higher_group.all_cards():
                    lower_group.add_exclude_card(card)

        # if TAG_FES in self.single_tag_card_groups:
        #     targets: List[SingleTagCardGroup] = []
        #     if TAG_UP in self.single_tag_card_groups:
        #         targets.append(self.single_tag_card_groups[TAG_UP])
        #     if TAG_RESIDENT in self.single_tag_card_groups:
        #         targets.append(self.single_tag_card_groups[TAG_RESIDENT])
            
        #     for target in targets:
        #         for card in self.single_tag_card_groups[TAG_FES].all_cards():
        #             target.add_exclude_card(card)

        # if TAG_UP in self.single_tag_card_groups:
        #     if TAG_RESIDENT not in self.single_tag_card_groups:
        #         return

        #     for card in self.single_tag_card_groups[TAG_UP].all_cards():
        #         self.single_tag_card_groups[TAG_RESIDENT].add_exclude_card(card)


class WishResult:
    """
    抽卡结果封装类
    """
    def __init__(self):
        self.cards: list[PackedCard] = []
        self.count = 0
        self.max_star = 0

    def add(self, packed_card: PackedCard):
        self.cards.append(packed_card)
        self.count += 1
        self.max_star = max(self.max_star, packed_card.card.star)
    
    def get_one(self) -> PackedCard:
        return self.cards[0]


@dataclass
class LogicResult:
    star: int
    type_: str
    tags: List[str] = field(default_factory=lambda: [TAG_RESIDENT])     # 卡片标签组 (卡片可同时属于多个标签组，但不同标签组之间有优先级)

    def __str__(self) -> str:
        return f"LogicResult({self.star}, '{self.type_}', {self.tags})"


if __name__ == '__main__':
    p = SingleTagCardGroup("test-resident")
    print(p)
    g = CardGroup("test", p)
    g.add_tag_group(TAG_UP)
    g.add_tag_group(TAG_FES)
    g.add_tag_group(TAG_APPOINT)
    print(g)
