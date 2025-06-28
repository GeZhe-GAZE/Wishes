r"""
Wishes v3.0
-----------

Module
_
    WishRecorder

Description
_
    Wishes 抽卡记录模块
"""


import os
import csv
import json
import datetime as dt
from Const import *
from Base import *
from dataclasses import dataclass


@dataclass
class CardCache:
    """
    单张卡片缓存
    """
    order: int                  # 累计抽数
    time: str                   # 时间
    packed_card: PackedCard     # 卡片信息

    def __str__(self) -> str:
        """
        返回 csv 格式的单行字符串
        """
        card = self.packed_card.card
        return ",".join((
            str(self.order),
            self.time,
            self.packed_card.real_tag,
            card.game,
            card.type,
            str(card.star),
            card.content
        ))


@dataclass
class IntervalCache:
    """
    间隔缓存
    """
    counter: int                # 间隔抽数
    packed_card: PackedCard     # 卡片信息

    def __str__(self) -> str:
        """
        返回 csv 格式的单行字符串
        """
        card = self.packed_card.card
        return ",".join((
            str(self.counter),
            self.packed_card.real_tag,
            card.game,
            card.type,
            str(card.star),
            card.content
        ))


class WishRecorder:
    """
    抽卡记录管理类
    管理单个卡池的抽卡记录
    *为方便解析，内部使用字符串表示星级
    """
    def __init__(self, record_dir: str, max_star: int):
        self.dir = record_dir

        # 总抽数
        self.total_counter = 0

        # 详细计数器记录
        # 层级: 标签 -> 类型 -> 星级 (字符串) -> 抽卡次数
        self.counters: Dict[str, Dict[str, Dict[str, int]]] = {}
        
        self.cache_list: List[CardCache] = []               # 缓存列表
        self.cache_size = CACHE_SIZE                        # 缓存大小

        self.max_star = max_star                            # 最高星级
        self.max_star_interval_counter = 0                  # 最高星级间隔抽数
        self.max_star_cache_list: List[IntervalCache] = []  # 最高星级缓存，只记录最高星级卡片

        if self._init_file():
            self.load_profile(self.dir)

    def _init_file(self) -> bool:
        """
        初始化文件，若文件已存在则不操作
        返回 profile 文件是否已存在
        """
        profile_path = os.path.join(self.dir, "profile.json")
        details_path = os.path.join(self.dir, "details.csv")
        interval_path = os.path.join(self.dir, "interval.csv")
        flag = True
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
            flag = False

        if not os.path.exists(profile_path):
            with open(profile_path, "w", encoding="utf-8") as f:
                data = {
                    "cache_size": self.cache_size,
                    "total": self.total_counter,
                    "max_star_interval": self.max_star_interval_counter,
                    "counters": self.counters,
                }
                json.dump(data, f, indent=4, ensure_ascii=False)
            flag = False
        
        if not os.path.exists(details_path):
            with open(details_path, "w", encoding="utf-8") as f:
                pass
        
        if not os.path.exists(interval_path):
            with open(interval_path, "w", encoding="utf-8") as f:
                pass
            
        return flag
    
    def _write_file(self):
        """
        将 profile数据 和 缓存 写入文件
        """
        profile_data = {
            "cache_size": self.cache_size,
            "total": self.total_counter,
            "max_star_interval": self.max_star_interval_counter,
            "counters": self.counters,
        }
        profile_path = os.path.join(self.dir, "profile.json")
        with open(profile_path, "w", encoding="utf-8", newline="") as f:
            json.dump(profile_data, f, indent=4, ensure_ascii=False)

        if self.cache_list:
            details_path = os.path.join(self.dir, "details.csv")
            with open(details_path, "a+", encoding="utf-8", newline="") as f:
                for row in self.cache_list:
                    f.write(str(row) + "\n")
            self.cache_list.clear()
        
        if self.max_star_cache_list:
            interval_path = os.path.join(self.dir, "interval.csv")
            with open(interval_path, "a+", encoding="utf-8", newline="") as f:
                for row in self.max_star_cache_list:
                    f.write(str(row) + "\n")
            self.max_star_cache_list.clear()
    
    def _reset_file(self):
        """
        重置文件数据
        """
        profile_data = {
            "cache_size": self.cache_size,
            "total": 0,
            "max_star_interval": 0,
            "counters": {},
        }
        profile_path = os.path.join(self.dir, "profile.json")
        with open(profile_path, "w", encoding="utf-8", newline="") as f:
            json.dump(profile_data, f, indent=4, ensure_ascii=False)

        details_path = os.path.join(self.dir, "details.csv")
        with open(details_path, "w", encoding="utf-8", newline="") as f:
            pass

        interval_path = os.path.join(self.dir, "interval.csv")
        with open(interval_path, "w", encoding="utf-8", newline="") as f:
            pass
    
    def load_profile(self, record_dir: str):
        """
        从 profile 文件中加载数据
        """
        profile_path = os.path.join(record_dir, "profile.json")
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        
        self.cache_size = profile_data["cache_size"]
        self.total_counter = profile_data["total"]
        self.max_star_interval_counter = profile_data["max_star_interval"]
        self.counters = profile_data["counters"]
        
    def add_record(self, packed_card: PackedCard):
        """
        追加单条记录
        """
        self.total_counter += 1
        self.max_star_interval_counter += 1
        
        if packed_card.real_tag not in self.counters:
            self.counters[packed_card.real_tag] = {}
        
        card = packed_card.card
        if card.type not in self.counters[packed_card.real_tag]:
            self.counters[packed_card.real_tag][card.type] = {}

        star_string = str(card.star)
        if star_string not in self.counters[packed_card.real_tag][card.type]:
            self.counters[packed_card.real_tag][card.type][star_string] = 0

        self.counters[packed_card.real_tag][card.type][star_string] += 1

        self.cache_list.append(CardCache(
            self.total_counter,
            f"{dt.datetime.now().replace(microsecond=0)}",
            packed_card,
        ))

        if card.star == self.max_star:
            self.max_star_cache_list.append(IntervalCache(
                self.max_star_interval_counter,
                packed_card
            ))
            self.max_star_interval_counter = 0
        
        if len(self.cache_list) >= self.cache_size:
            self._write_file()

    def clear(self):
        """
        清除记录
        """
        self.total_counter = 0
        self.max_star_interval_counter = 0
        self.counters = {}

        self.cache_list = []
        self.max_star_cache_list = []
        
        self._reset_file()

    # TODO: 查询 details 记录和 interval 记录