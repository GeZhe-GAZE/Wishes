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
from dataclasses import dataclass


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
    def __init__(self, card: Card, is_up: bool = False, is_appoint: bool = False) -> None:
        self.card = card
        self.is_up = is_up              # 在当前卡组中是否为 UP
        self.is_appoint = is_appoint    # 在当前卡组中是否为 定轨
    
    def __str__(self) -> str:
        return f"PackedCard({self.card}, {self.is_up}, {self.is_appoint})"


class CardGroup:
    """
    卡组类，根据卡片星级管理卡片
    确保卡组内的卡片不相同
    """
    def __init__(self, name: str, version: str = "", is_official: bool = False):
        self.name = name                    # 卡组名称
        self.is_official = is_official      # 是否为官方卡组
        self.version = version              # 卡组版本，仅在官方卡组内可用
        
        # 卡池管理结构
        self.cards: Dict[str, Dict[str, Dict[int, Dict[str, Card]]]] = {"resident": {}}
        # 最高星级 (最高稀有度)
        self.max_star = 0
        # 卡片总数
        self.count = 0
    
    def __str__(self) -> str:
        cards_info = ""
        for tag, tag_dict in self.cards.items():
            cards_info += f"- {tag}\n"
            for type_, type_dict in tag_dict.items():
                cards_info += f"-   {type_}\n"
                for star, card_dict in type_dict.items():
                    cards_info += f"-     Star{star}\n"
                    cards_info += "\n".join([str(card) for card in card_dict.values()])

        return "\n".join((
            f"CardGroup <{self.name}>",
            f"version: {self.version if self.version else "no-version"}  is_official: {self.is_official}",
            f"count: {self.count}",
            "cards:",
            cards_info
        ))

    def add_up(self):
        self.cards["up"] = {}

    def add_star(self, star: int, type_: str, is_up: bool = False):
        self.cards["up" if is_up else "resident"][type_][star] = {}
        self.max_star = max(self.max_star, star)
    
    def add_card(self, card: Card, is_up: bool = False):
        """
        添加卡片
        """
        target = self.cards["up" if is_up else "resident"][card.type][card.star]
        if card.content not in target:
            target[card.content] = card
            self.count += 1
    
    def random_card(self, type_: str, star: int, is_up: bool = False) -> Card:
        """
        等概率抽取一个卡片
        """
        return choice(tuple(self.cards["up" if is_up else "resident"][type_][star].values()))
    
    def remove_card(self, type_: str, star: int, content: str, is_up: bool = False):
        """
        删除卡片
        """
        target = self.cards["up" if is_up else "resident"][type_][star]
        if content in target:
            del target[content]


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
    is_up: bool = False
    is_fes: bool = False

    def __str__(self) -> str:
        return f"LogicResult({self.star}, '{self.type_}', {self.is_up}, {self.is_fes})"
