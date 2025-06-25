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
from WishLogic import new_logic
from WishRule import tag_to_rule_class, WishLogic
from typing import Dict, List, Sequence


class CardSystem:
    """
    卡片管理系统
    """
    def __init__(self, cards_dir: str, dir_config: Dict[str, Dict[str, Sequence[int]]]):
        # 卡片管理层级：游戏 -> 类型 -> 星级 -> 卡片名称: 卡片对象
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


class CardGroupSystem:
    """
    卡组管理系统
    """
    def __init__(self, card_group_dir: str, card_system: CardSystem):
        self.card_groups: dict[str, CardGroup] = {}
        self.card_system = card_system

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
            data = json.load(f)
        group = CardGroup(data["name"], data["version"], data["is_official"])

        # 加载 UP
        for star in ("Star5", "Star4"):
            for card_info in data["up"][star]:
                card_info: str
                card = self.card_system.get_card(card_info)
                if card.usable():
                    group.add_card(card, True)
                    continue
                # 卡片不在系统中，尝试从 json 文件加载
                if card_info.endswith(".json") and os.path.exists(card_info):
                    group.add_card(Card.load_from_json(card_info), True)

        # 加载常驻
        with open(data["resident"], "r", encoding="utf-8") as f:
            resident_data = json.load(f)
        for type_ in (TYPE_ROLE, TYPE_WEAPON):
            for star in (5, 4, 3):
                if type_ == TYPE_ROLE and star == 3:
                    continue
                for card_info in resident_data[type_][f"Star{star}"]:
                    card_info: str
                    card = self.card_system.get_card(card_info)
                    if card.usable():
                        group.add_card(card, False)
                        continue
                    if card_info.endswith(".json") and os.path.exists(card_info):
                        group.add_card(Card.load_from_json(card_info), False)

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
        return self.card_groups[name]


class CardPoolSystem:
    """
    卡池管理系统
    """
    def __init__(self, card_pool_dir: str, card_group_system: CardGroupSystem) -> None:
        self.card_pool_dir = card_pool_dir
        self.card_pool_group: dict[str, CardPool] = {}
        self.card_group_system = card_group_system

        for filename in os.listdir(self.card_pool_dir):
            file = os.path.join(self.card_pool_dir, filename)
            self.load_card_pool(file)
    
    def end(self):
        """
        程序退出，通知所有 CardPool
        """
        for card_pool in self.card_pool_group.values():
            card_pool.end()
            filename = os.path.join(self.card_pool_dir, f"{card_pool.name}.json")
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            logic = card_pool.logic

            data["logic_config"]["counter"][STAR_5] = logic.counter[5]
            data["logic_config"]["counter"][STAR_4] = logic.counter[4]
            data["logic_config"]["probability"][STAR_5] = logic.probability[5]
            data["logic_config"]["probability"][STAR_4] = logic.probability[4]
            data["logic_config"]["next_up"][STAR_5] = logic.next_up[5]
            data["logic_config"]["next_up"][STAR_4] = logic.next_up[4]

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
    
    def load_card_pool(self, card_pool_config_file: str):
        """
        从卡池配置文件中加载卡池
        """
        with open(card_pool_config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        name = data["name"]
        logic = new_logic(data["game"], data["type"])
        card_group_info: str = data["card_group"]

        if self.card_group_system.has_group(card_group_info):
            card_group = self.card_group_system.get_group(card_group_info)
        else:
            if card_group_info.endswith(".json") and os.path.exists(card_group_info):
                card_group = self.card_group_system.load_group_from_json(card_group_info)
            else:
                card_group = CardGroup("")
        card_group.exclude_same_card()

        logic_config = data["logic_config"]
        logic.counter[5] = logic_config["counter"][STAR_5]
        logic.counter[4] = logic_config["counter"][STAR_4]
        logic.probability[5] = logic_config["probability"][STAR_5]
        logic.probability[4] = logic_config["probability"][STAR_4]
        logic.next_up[5] = logic_config["next_up"][STAR_5]
        logic.next_up[4] = logic_config["next_up"][STAR_4]

        card_pool = CardPool(name, logic, card_group, data["record_dir"])
        self.card_pool_group[name] = card_pool
    
    def has_card_pool(self, name: str) -> bool:
        """
        检查是否包含某个卡池
        """
        return name in self.card_pool_group.keys()
    
    def get_card_pool(self, name: str) -> CardPool:
        """
        根据名称获取卡池
        """
        return self.card_pool_group[name]


class WishRuleSystem:
    """
    抽卡逻辑管理系统
    """
    def __init__(self, rule_config_dir: str) -> None:
        self.dir = rule_config_dir
        self.logics: Dict[str, WishLogic] = {}

        try: 
            for filename in os.listdir(self.dir):
                if filename.endswith(".json"):
                    logic = self.load_logic(os.path.join(self.dir, filename))
                    self.logics[logic.name] = logic
        except:
            pass
    
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
