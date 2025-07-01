r"""
Wishes v3.0
-----------

Module
_
    Const

Description
_
    Wishes 常量定义
"""

# NOTE: Wishes 基本信息
VERSION = "v3.0.1"

# NOTE: 抽卡部分
MAX_PROBABILITY = 10000

# NOTE: 卡组内卡片分类标签
TAG_UP = "up"               # UP 组
TAG_FES = "fes"             # Fes 组, 包含于 UP 组
TAG_APPOINT = "appoint"     # Appoint (定轨) 组, 包含于 UP 组和 Fes 组
TAG_STANDARD = "standard"   # 常驻组

# NOTE: 记录模块缓存大小
CACHE_SIZE = 10
