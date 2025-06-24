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


class WishRecorder:
    """
    抽卡记录管理类
    """
    def __init__(self, record_dir: str):
        self.dir = record_dir

        self.total_counter = 0
        self.interval_5_counter = 0
        self.up_counter: dict[int, int] = {
            5: 0,
            4: 0,
        }
        self.resident_counter: dict[str, dict[int, int]] = {
            TYPE_ROLE: {
                5: 0,
                4: 0,
            },
            TYPE_WEAPON: {
                5: 0,
                4: 0,
                3: 0,
            }
        }
        # 缓存列表
        # 每个缓存内容：(抽数, 时间, 类型, 星级, 内容)
        self.cache_cards: list[tuple[int, str, str, int, str]] = []
        # 五星间隔缓存：(间隔抽数, 内容, 是否 UP)
        self.cache_star_5: list[tuple[int, str, bool]] = []
        self.cache_size = 10

        if self._init_file():
            self.load(self.dir)

    def _init_file(self) -> bool:
        """
        初始化文件，若文件已存在则不操作
        返回文件是否已存在
        """
        profile_path = os.path.join(self.dir, "profile.json")
        details_path = os.path.join(self.dir, "details.csv")
        interval_path = os.path.join(self.dir, "interval.csv")
        flag = True
        if not os.path.exists(profile_path):
            with open(profile_path, "w", encoding="utf-8") as f:
                data = {
                    "total": self.total_counter,
                    "interval_5": self.interval_5_counter,
                    "up": {
                        STAR_5: self.up_counter[5],
                        STAR_4: self.up_counter[4],
                    },
                    "resident": {
                        TYPE_ROLE: {
                            STAR_5: self.resident_counter[TYPE_ROLE][5],
                            STAR_4: self.resident_counter[TYPE_ROLE][4],
                        },
                        TYPE_WEAPON: {
                            STAR_5: self.resident_counter[TYPE_WEAPON][5],
                            STAR_4: self.resident_counter[TYPE_WEAPON][4],
                            STAR_3: self.resident_counter[TYPE_WEAPON][3],
                        }
                    },
                }
                json.dump(data, f, indent=4, ensure_ascii=False)
            flag = False
        
        if not os.path.exists(details_path):
            with open(details_path, "w", encoding="utf-8") as f:
                pass
            flag = False
        
        if not os.path.exists(interval_path):
            with open(interval_path, "w", encoding="utf-8") as f:
                pass
            flag = False
            
        return flag
    
    def _write_file(self):
        """
        将数据写入文件
        """
        profile_data = {
            "total": self.total_counter,
            "interval_5": self.interval_5_counter,
            "up": {
                STAR_5: self.up_counter[5],
                STAR_4: self.up_counter[4],
            },
            "resident": {
                TYPE_ROLE: {
                    STAR_5: self.resident_counter[TYPE_ROLE][5],
                    STAR_4: self.resident_counter[TYPE_ROLE][4],
                },
                TYPE_WEAPON: {
                    STAR_5: self.resident_counter[TYPE_WEAPON][5],
                    STAR_4: self.resident_counter[TYPE_WEAPON][4],
                    STAR_3: self.resident_counter[TYPE_WEAPON][3],
                }
            },
        }
        profile_path = os.path.join(self.dir, "profile.json")
        with open(profile_path, "w", encoding="utf-8", newline="") as f:
            json.dump(profile_data, f, indent=4, ensure_ascii=False)

        details_path = os.path.join(self.dir, "details.csv")
        with open(details_path, "a+", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for row in self.cache_cards:
                writer.writerow(row)
            self.cache_cards.clear()

        if self.cache_star_5:
            interval_path = os.path.join(self.dir, "interval.csv")
            with open(interval_path, "a+", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for row in self.cache_star_5:
                    writer.writerow(row)
                self.cache_star_5.clear()
    
    def _reset_file(self):
        """
        重置文件内容
        """
        profile_data = {
            "total": self.total_counter,
            "interval_5": self.interval_5_counter,
            "up": {
                STAR_5: self.up_counter[5],
                STAR_4: self.up_counter[4],
            },
            "resident": {
                TYPE_ROLE: {
                    STAR_5: self.resident_counter[TYPE_ROLE][5],
                    STAR_4: self.resident_counter[TYPE_ROLE][4],
                },
                TYPE_WEAPON: {
                    STAR_5: self.resident_counter[TYPE_WEAPON][5],
                    STAR_4: self.resident_counter[TYPE_WEAPON][4],
                    STAR_3: self.resident_counter[TYPE_WEAPON][3],
                }
            },
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
    
    def load(self, record_dir: str):
        """
        从文件中加载数据
        """
        profile_path = os.path.join(record_dir, "profile.json")
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        
        self.total_counter = profile_data["total"]
        self.interval_5_counter = profile_data["interval_5"]
        self.up_counter[5] = profile_data["up"][STAR_5]
        self.up_counter[4] = profile_data["up"][STAR_4]
        self.resident_counter[TYPE_ROLE][5] = profile_data["resident"][TYPE_ROLE][STAR_5]
        self.resident_counter[TYPE_ROLE][4] = profile_data["resident"][TYPE_ROLE][STAR_4]
        self.resident_counter[TYPE_WEAPON][5] = profile_data["resident"][TYPE_WEAPON][STAR_5]
        self.resident_counter[TYPE_WEAPON][4] = profile_data["resident"][TYPE_WEAPON][STAR_4]
        self.resident_counter[TYPE_WEAPON][3] = profile_data["resident"][TYPE_WEAPON][STAR_3]
        
    def add_record(self, card: Card):
        """
        追加单条记录
        """
        self.total_counter += 1
        self.interval_5_counter += 1
        if card.up:
            self.up_counter[card.star] += 1
        else:
            self.resident_counter[card.type][card.star] += 1

        self.cache_cards.append((
            self.total_counter,
            f"{dt.datetime.now().replace(microsecond=0)}",
            card.type,
            card.star,
            card.content
        ))
        if card.star == 5:
            self.cache_star_5.append((
                self.interval_5_counter,
                card.content,
                card.up
            ))
            self.interval_5_counter = 0


        if len(self.cache_cards) >= self.cache_size:
            self._write_file()

    def clear(self):
        """
        清除记录
        """
        self.total_counter = 0
        self.interval_5_counter = 0
        self.up_counter: dict[int, int] = {
            5: 0,
            4: 0,
        }
        self.resident_counter: dict[str, dict[int, int]] = {
            TYPE_ROLE: {
                5: 0,
                4: 0,
            },
            TYPE_WEAPON: {
                5: 0,
                4: 0,
                3: 0,
            }
        }
        self.cache_cards: list[tuple[int, str, str, int, str]] = []
        self.cache_star_5: list[tuple[int, str, bool]] = []
        self._reset_file()
