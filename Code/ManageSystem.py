r"""
Wishes v3.0
-----------

Module
_
    ManageSystem

Description
_
    定义 Wishes 中的各种管理系统
"""


import os
import json
from Const import *
from Base import *
from CardPool import CardPool
from WishRecorder import WishRecorder
from WishRule import WishLogic
from WishRule import tag_to_rule_class, WishLogic
from typing import Dict, List, Sequence


class CardSystem:
    """
    卡片管理系统
    卡片管理层级: 游戏 -> 类型 -> 星级 -> 卡片名称: 卡片对象
    """
    def __init__(self, cards_dir: str, dir_config: Dict[str, Dict[str, Sequence[int]]]):
        self.card_container: Dict[str, Dict[str, Dict[int, Dict[str, Card]]]] = {
            game: {
                type_: {
                    star: self.load_cards(os.path.join(cards_dir, game, type_, f"Star{star}"))
                    for star in star_list
                }
                for type_, star_list in type_dict.items()
            }
            for game, type_dict in dir_config.items()
        }
    
    @staticmethod
    def load_cards(dir_path: str) -> Dict[str, Card]:
        """
        静态加载卡片方法
        加载指定目录下的所有卡片 json 文件为 卡片名称: 卡片对象 键值对并返回
        """
        cards = {}
        for filename in os.listdir(dir_path):
            if filename.endswith(".json"):
                filepath = os.path.join(dir_path, filename)
                card = Card.load_from_json(filepath)
                cards[card.content] = card
        return cards
    
    def get_card(
            self,
            content: str,         # 指定卡片内容进行查找
            game: str | None = None,    # 通过指定更多信息进行快速查找
            type_: str | None = None,
            star: int | None = None
            ) -> Card:
        """
        查找卡片并返回
        通过指定 game, type_, star 等可选过滤条件快速查找
        若系统中存在相同 content 的卡片，则只返回第一个匹配的卡片
        若没有匹配的卡片，则返回空卡片: Card.none()
        """
        # 当提供全部过滤条件时，尝试精确查找
        if all((game, type_, star)):
            try:
                return self.card_container[game][type_][star][content] # type: ignore
            except KeyError:
                return Card.none()
        
        # 确定搜索游戏范围
        games = [game] if game and game in self.card_container else self.card_container.keys()

        for g in games:
            # 确定类型搜索范围
            types = [type_] if type_ and type_ in self.card_container[g] else self.card_container[g].keys()

            for t in types:
                # 确定星级搜索范围
                stars = [star] if star and star in self.card_container[g][t] else self.card_container[g][t].keys()

                for s in stars:
                    # 在当前星级中查找卡片
                    card_dict = self.card_container[g][t][s]
                    if content in card_dict:
                        return card_dict[content]   # 找到

        # 未找到
        return Card.none()
    
    def has_card(self, card: Card) -> bool:
        """
        判断卡片是否存在于系统中
        """
        if not card.usable():   # 空卡片不存在
            return False
        return card == self.get_card(card.content, card.game, card.type, card.star)
    
    def add_card(self, card: Card):
        """
        添加卡片到系统中
        """
        if self.has_card(card):     # 检验卡片是否已存在
            return
        
        # 确定卡片所属游戏是否存在
        if card.game not in self.card_container:
            self.card_container[card.game] = {card.type: {card.star: {card.content: card}}}     # 不存在，直接添加
            return
        game_dict = self.card_container[card.game]

        # 确定卡片类型在该游戏中是否存在
        if card.type not in game_dict:
            game_dict[card.type] = {card.star: {card.content: card}}
            return
        type_dict = game_dict[card.type]

        # 确定卡片星级在该类型中是否存在
        if card.star not in type_dict:
            type_dict[card.star] = {card.content: card}
            return
        # 最终添加卡片
        type_dict[card.star][card.content] = card
    
    def games(self) -> List[str]:
        """
        返回系统中所有游戏的名称列表
        """
        return list(self.card_container.keys())
    
    def types(self, game: str) -> List[str]:
        """
        返回指定游戏中所有卡片类型的名称列表
        """
        return list(self.card_container[game].keys())
    
    def stars(self, game: str, type_: str) -> List[int]:
        """
        返回指定游戏和类型中所有卡片星级的列表
        """
        return list(self.card_container[game][type_].keys())


class ResidentGroupSystem:
    """
    常驻卡组管理系统
    """
    def __init__(self, card_group_dir: str, card_system: CardSystem):
        self.card_groups: dict[str, SingleTagCardGroup] = {}
        self.card_system = card_system

        for filename in os.listdir(card_group_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(card_group_dir, filename)
                group = self.load_group_from_json(filepath)
                self.card_groups[group.name] = group

    def load_group_from_json(self, file: str) -> SingleTagCardGroup:
        """
        从 json 文件中加载常驻卡组
        """
        with open(file, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        group = SingleTagCardGroup(config["name"])
        del config["name"]

        card_info_dicts = (
            card_info_dict
            for star_dict in config.values()
            for card_info_list in star_dict.values()
            for card_info_dict in card_info_list
        )

        for card_info_dict in card_info_dicts:
            if "type" in card_info_dict:
                card_info_dict["type_"] = card_info_dict["type"]
                del card_info_dict["type"]
            card = self.card_system.get_card(**card_info_dict)
            if card.usable():
                group.add_card(card)
        
        return group
    
    def get_group(self, name: str) -> SingleTagCardGroup:
        """
        获取指定名称的常驻卡组
        """
        if name not in self.card_groups:
            return SingleTagCardGroup("empty-group")
        return self.card_groups[name]


class CardGroupSystem:
    """
    卡组管理系统
    """
    def __init__(self, card_group_dir: str, card_system: CardSystem, resident_group_system: ResidentGroupSystem):
        self.card_groups: dict[str, CardGroup] = {}
        self.card_system = card_system                          # 卡片系统
        self.resident_group_system = resident_group_system      # 常驻卡组管理系统

        for filename in os.listdir(card_group_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(card_group_dir, filename)
                group = self.load_group_from_json(filepath)
                self.card_groups[group.name] = group

    def load_group_from_json(self, file: str) -> CardGroup:
        """
        从 json 文件中加载卡组
        """
        with open(file, "r", encoding="utf-8") as f:
            config = json.load(f)

        group = CardGroup(
            config["name"],
            self.resident_group_system.get_group(config[TAG_RESIDENT]),     # 常驻卡组
            version=config["version"],
            is_official=config["is_official"]
        )

        # 加载其他卡片 (UP, Fes, Appoint)
        for tag in (TAG_UP, TAG_FES, TAG_APPOINT):
            if tag in config:
                tag_group = self.load_single_group_from_config(config[tag], f"{group.name}-{tag}")
                group.add_tag_group(tag, tag_group)

        return group
    
    def load_single_group_from_config(self, config: Dict[str, Dict[int, List[Dict]]], name: str = "") -> SingleTagCardGroup:
        """
        从配置字典中加载单标签卡组
        """
        group = SingleTagCardGroup(name)

        cards_info_dicts = (
            card_info_dict
            for star_dict in config.values()
            for card_info_list in star_dict.values()
            for card_info_dict in card_info_list
        )

        for card_info_dict in cards_info_dicts:
            if "type" in card_info_dict:
                card_info_dict["type_"] = card_info_dict["type"]
                del card_info_dict["type"]
            card = self.card_system.get_card(**card_info_dict)
            if card.usable():
                group.add_card(card)
        
        return group
    
    def has_group(self, name: str) -> bool:
        """
        检查是否包含某个卡组
        """
        return name in self.card_groups.keys()
    
    def get_group(self, name: str) -> CardGroup:
        """
        根据名称获取卡组
        """
        if name not in self.card_groups:
            return CardGroup("empty-group")
        return self.card_groups[name]


class WishLogicSystem:
    """
    抽卡逻辑管理系统
    """
    def __init__(self, logic_config_dir: str) -> None:
        self.dir = logic_config_dir
        # 管理层级: 抽卡逻辑名称: 抽卡逻辑对象 (模板原型)
        self.logics: Dict[str, WishLogic] = self.load_all_logics(logic_config_dir)
        
    def load_all_logics(self, rule_config_dir: str) -> Dict[str, WishLogic]:
        """
        从指定目录加载所有抽卡逻辑
        """
        logics: Dict[str, WishLogic] = {}
        for filename in os.listdir(rule_config_dir):
            try:
                if filename.endswith(".json"):
                    logic = self.load_logic(os.path.join(rule_config_dir, filename))
                    logics[logic.name] = logic
            except Exception as e:
                print(f"WishRuleSystem: {filename} 加载失败: {e}")
        
        return logics
    
    def load_logic(self, rule_config_file: str) -> WishLogic:
        """
        从 json 文件中加载抽卡逻辑
        """
        with open(rule_config_file, "r", encoding="utf-8") as f:
            config: Dict = json.load(f)
        
        for key in config.keys():
            if key == "name":
                continue
            if key == "rules":
                rule_tags: List[str] = config[key]
                config[key] = [tag_to_rule_class(tag) for tag in rule_tags]
                continue
            for star_key in tuple(config[key]):
                star_key: str
                if star_key.isdigit():
                    config[key][int(star_key)] = config[key][star_key]
                    del config[key][star_key]
        
        return WishLogic(config)
    
    def get_logic(self, name: str) -> WishLogic:
        """
        根据名称获取抽卡逻辑实例 (副本)
        """
        if name not in self.logics:
            return WishLogic.none()
        return self.logics[name]


class CardPoolSystem:
    """
    卡池管理系统
    """
    def __init__(self, card_pool_dir: str, card_group_system: CardGroupSystem, wish_logic_system: WishLogicSystem) -> None:
        self.card_pool_dir = card_pool_dir
        # 管理层级: 卡池名称: 卡池对象
        self.card_pool_group: dict[str, CardPool] = {}
        self.card_group_system = card_group_system
        self.wish_logic_system = wish_logic_system

        for filename in os.listdir(self.card_pool_dir):
            file = os.path.join(self.card_pool_dir, filename)
            self.load_card_pool(file)
    
    def load_card_pool(self, card_pool_config_file: str) -> CardPool:
        """
        从卡池配置文件中加载卡池
        """
        with open(card_pool_config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        name = data["name"]
        card_group = self.card_group_system.get_group(data["card_group"])
        logic = self.wish_logic_system.get_logic(data["logic"])

        logic_state = data["logic_state"]
        logic.load_state(logic_state)       # 加载抽卡逻辑状态

        card_pool = CardPool(name, logic, card_group, data["recorder_dir"])
        self.card_pool_group[name] = card_pool

        return card_pool
    
    def save_card_pool(self, name: str, file: str):
        """
        保存卡池至 json 文件
        """
        card_pool = self.get_card_pool(name)
        if card_pool.none_flag:
            return
        
        data = {
            "name": card_pool.name,
            "card_group": card_pool.card_group.name,
            "logic": card_pool.logic.name,
            "recorder_dir": card_pool.recorder.dir,
            "logic_state": card_pool.get_logic_state()
        }

        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def has_card_pool(self, name: str) -> bool:
        """
        检查是否包含某个卡池
        """
        return name in self.card_pool_group.keys()
    
    def get_card_pool(self, name: str) -> CardPool:
        """
        根据名称获取卡池
        """
        if name not in self.card_pool_group:
            return CardPool.none()
        return self.card_pool_group[name]
    
