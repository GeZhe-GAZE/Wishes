# Wishes 🌠

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![JSON](https://img.shields.io/badge/Data-JSON-000000?logo=json&logoColor=white)]()
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
[![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github)](https://github.com)
[![VSCode](https://img.shields.io/badge/IDE-VSCode-007ACC?logo=visual-studio-code)](https://code.visualstudio.com/)
[![nuitka](https://img.shields.io/badge/Compiler-nuitka-008000?logo=nuitka&logoColor=white)](https://nuitka.net)


## 中文

`Wishes` 是一个**高度自定义、高度适配性**的模拟游戏抽卡工具。<br>
期望实现的主要功能：
- 模拟抽卡算法
- 实现带人物/物品立绘图片和动画效果的抽卡
- 抽卡记录和抽卡结果分析
- 自定义卡池和管理卡池/卡组/卡片的功能

---

#### 重要提醒
以 [Python](https://www.python.org/)`3.13` 作为主要开发语言。<br>

项目目前正处于**底层开发阶段**，仅可在命令行中测试并运行，后续将引入 [Qt6](https://www.qt.io/) 及使用 `Qt Quick` 开发的图形界面。

---

## 开始使用
下载最新发行版 `Wishes v3.0.1` 压缩包，解压后运行 `Wishes.exe` 即可。[GitHub Release](https://github.com/GeZhe-GAZE/Wishes/releases) <br>

或者，从 GitHub 仓库克隆项目，运行 `main_command_line.py` 即可。[GitHub Repository](https://github.com/GeZhe-GAZE/Wishes)

```bash
python main_command_line.py
```

## 自定义拓展
`Wishes v3` 除模拟抽卡过程外，最重要的功能便是**自定义拓展**。<br>

仅通过 `json` 文件的相关配置，即可实现自定义**卡片、卡组、抽卡逻辑、卡池**等内容。<br>

以下为详细的配置流程:

### 1. 卡片配置
卡片配置文件为 `json` 格式，位于 `Data/Cards` 目录中，文件名任意，但必须以 `.json` 结尾。<br>
路径结构为：**Data/Cards/<游戏>/<类型>/<星级>/*.json** <br>

每个 `json` 卡片配置文件代表一张卡片，每个文件需包含以下字段：

- **content**：卡片内容名称
- **game**：卡片所属游戏
- **type**：卡片类型，如 `角色`、`武器` 等
- **star**：卡片星级，必须为整数
- **attribute**: 卡片属性，如 `冰`、`火`、`风` 等
- **title**: 卡片称号，用于抽卡界面显示 **(现版本未启用)**
- **profession**: 卡片职业类型，如 `智识`、`单手剑`、`击破` 等
- **image_path**: 卡片立绘图片路径，相对于 `Wishes` 目录

添加卡片后，还需在 `Data/Config/CardsDirConfig.json` 中注册目录结构。

#### 卡片配置示例
```json
{
    "content": "胡桃",
    "game": "Genshin",
    "star": 5,
    "type": "Character",
    "attribute": "火",
    "title": "",
    "profession": "长柄武器",
    "image_path": "Data/Images/Genshin/Character/Star5/胡桃.png"
}
```

#### 目录结构配置示例
```json
{
    "Genshin": {
        "Character": [5, 4],
        "Weapon": [5, 4, 3]
    },
    "StarRail": {
        "Character": [5, 4],
        "Weapon": [5, 4, 3]
    },
    "ZZZ": {
        "Character": [5, 4],
        "Weapon": [5, 4, 3],
        "Bangboo": [5, 4]
    }
}
```

### 2. 卡组配置
`Wishes` 中的卡组分为**常驻卡组**和**正式卡组**，常驻卡组可视作正式卡组的一部分。因为通常情况下常驻卡组会同时被多个正式卡组使用，因此常驻卡组被作为**独立卡组**进行配置，而正式卡组仅需**引用所需的常驻卡组**，再包含一些**特殊的、额外的卡片**即可使用。<br>

#### 2.1 常驻卡组配置
所有的常驻卡组都在 `Data/StandardGroups` 目录中配置，文件名任意，但必须以 `.json` 结尾。<br>

每个 `json` 常驻卡组配置文件代表一个常驻卡组，每个文件需包含以下字段：

- **name**：常驻卡组名称，且为**唯一标识符**
- **类型 -> 星级 -> 卡片组**，表示该常驻卡组中该类型下，包含的星级，以及该星级下包含的卡片，每一个卡片对象都需包含以下字段：
  - **game**：卡片所属游戏
  - **type**：卡片类型
  - **star**：卡片星级
  - **content**：卡片内容名称

> **类型 -> 星级 -> 卡片组**的数量不限，但需保证同类型下、同星级下，**卡片内容名称**不重复，否则多余的卡片将被覆盖。

#### 常驻卡组配置示例
```json
{
    "name": "崩坏：星穹铁道-角色-常驻-单标签卡组",
    "Character": {
        "5": [
            {
                "game": "StarRail",
                "type": "Character",
                "star": 5,
                "content": "克拉拉"
            },
            {
                "game": "StarRail",
                "type": "Character",
                "star": 5,
                "content": "姬子"
            },
            ...
        ],
        "4": [
            {
                "game": "StarRail",
                "type": "Character",
                "star": 4,
                "content": "三月七"
            },
            {
                "game": "StarRail",
                "type": "Character",
                "star": 4,
                "content": "丹恒"
            },
            ...
        ]
    },
    "Weapon": {
        "4": [
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 4,
                "content": "「我」的诞生"
            },
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 4,
                "content": "一场术后对话"
            },
            ...
        ],
        "3": [
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 3,
                "content": "乐圮"
            },
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 3,
                "content": "俱殁"
            },
            ...
        ]
    }
}
```

#### 2.2 正式卡组配置
所有的正式卡组都在 `Data/CardGroups` 目录中配置，文件名任意，但必须以 `.json` 结尾。<br>

每个 `json` 正式卡组配置文件代表一个正式卡组，每个文件需包含以下字段：

- **name**：正式卡组名称，且为**唯一标识符**
- **version**: 卡组版本，特用于官方卡池的配置，在当前版本中无实际作用
- **is_official**: 标注是否为官方卡池，在当前版本中无实际作用
- **standard**: 引用的常驻卡组名称，需在 `Data/StandardGroups` 目录中存在
- **exclude**: 是否启用**排除模式**，启用后，常驻卡组将视作**不包含**正式卡组中的卡片
- 正式卡组中，**除常驻卡组外，额外添加的卡片**，以**标签组**的方式进行分类，标签组内部再次按照 **类型 -> 星级 -> 卡片组** 的方式进行分类，每一个卡片对象都需包含以下字段：
  - **game**：卡片所属游戏
  - **type**：卡片类型
  - **star**：卡片星级
  - **content**：卡片内容名称

当前可供选择的标签组有:
- **up 组**: UP 卡片组，包含的卡片将作为 UP 卡片，特用于包含 UP 相关抽卡逻辑的卡池
- **fes 组**: Fes 卡片组，包含的卡片将作为 Fes 卡片，特用于包含 Fes 相关抽卡逻辑的卡池
- **appoint 组**: Appoint 卡片组，包含的卡片将作为 Appoint 卡片，特用于包含 Appoint (定轨) 相关抽卡逻辑的卡池
- **standard 组**: 实际上已在常驻卡组中配置，因此无需在正式卡组中额外配置，包含的卡片将作为常驻卡片

**注意**: 这些标签组在文件中必须**小写**，否则将无法识别。

#### 正式卡组配置示例
```json
{
    "name": "默认卡组2",
    "version": "v3.3",
    "is_official": true,
    "standard": "崩坏：星穹铁道-角色-常驻-单标签卡组",
    "exclude": true,
    "up": {
        "Character": {
            "5": [
                {
                    "game": "StarRail",
                    "star": 5,
                    "type": "Character",
                    "content": "风堇"
                }
            ],
            "4": [
                {
                    "game": "StarRail",
                    "star": 4,
                    "type": "Character",
                    "content": "米沙"
                },
                {
                    "game": "StarRail",
                    "star": 4,
                    "type": "Character",
                    "content": "希露瓦"
                },
                {
                    "game": "StarRail",
                    "star": 4,
                    "type": "Character",
                    "content": "娜塔莎"
                }
            ]
        }
    }
}
```

### 3. 抽卡逻辑配置
所有的抽卡逻辑都在 `Data/LogicConfig` 目录中配置，文件名任意，但必须以 `.json` 结尾。<br>

每个 `json` 抽卡逻辑配置文件代表一个抽卡逻辑，每个文件需包含以下字段：

- **name**：抽卡逻辑名称，且为**唯一标识符**
- **rules**: 抽卡逻辑规则表，或称之为**规则链**，其中按顺序配置不同的**抽卡规则项**，每个规则项都具有不同的功能和相应的配置项

**注意**: 规则链中，**规则项的顺序**非常重要，因为在每一次抽卡过程中，规则链将**按照顺序依次执行规则项**，确定抽卡结构，在抽卡结束后，再次**按照顺序依次回调规则项**。若非特别说明，以下规则项的个操作都在**执行**中完成。

#### 规则项介绍
目前，可供选用的 **14** 个规则项为:

- **StarCounterRule**: **星级计数规则**，用于统计抽卡过程中，**不同星级卡片的抽卡次数**，以供其他规则使用。计数器会在抽出对应星级后重置，且计数器的更新在回调中完成。因此，无论该规则项被置于规则链中的任何位置，其都能正常工作，但**一般置于规则链首部**。<br> 
包含以下配置项:

  - **star_list**: 需要统计星级计数的列表，如 `[5, 4, 3]`，表示需要统计 5 星、4 星、3 星卡片的抽卡次数


- **TypeStarCounterRule**: **基于星级的类型计数器规则**，统计**每个星级下各类型的抽卡计数**，以供其他规则使用。计数器会在抽出对应星级下的对应类型后重置，且计数器的更新在回调中完成。因此，无论该规则项被置于规则链中的任何位置，其都能正常工作，但**一般置于规则链首部**。<br>
包含以下配置项:

  - **type_star_dict**: 需要类型计数的字典，如 `{"5": ["Character", "Weapon"]}` ，表示需要统计 5 星角色和 5 星武器的抽卡次数
  
  **注意**: 每次抽卡后，仅有**当前抽星级下的计数器**会更新，其他星级的计数器不会更新。<br>


- **StarProbabilityRule**: **星级概率规则**，用于根据星级概率表，随机抽取对应星级卡片。每次回调时，都会重置当前概率为基础概率。<br>
包含以下配置项:

  - **star_probability**: 星级概率权重表，如 `{"5": 60, "4": 510, "3": 9430}`，表示 5 星卡片的基础概率为 0.6%，4 星卡片的基础概率为 5.1%，3 星卡片的基础概率为 94.3%。<br>

  **注意**: `Wishes` 采用**整数概率权重**，以避免浮点数导致的精度问题。因此，在配置时，需要将概率**乘以 10000**，如 0.6% 的概率需配置为 60，5.1% 的概率需配置为 510，94.3% 的概率需配置为 9430。配置时，尽量保证**各星级概率之和为 10000**。


- **TypeStarProbabilityRule**: **基于星级的类型基础概率规则**，根据当前星级，和星级对应的类型概率权重决定当前抽类型。必须在确定当前抽星级后使用，才能正常工作。<br>
包含以下配置项:

  - **type_probability**: 类型星级概率权重表，如 `{"5": {"Character": 10000}`, 表示 5 星卡片中，角色卡片的概率为 100%，且不包含其他类型卡片。


- **StarPityRule**: **星级保底规则**，提供对应星级的保底，若抽卡次数达到阈值，则触发保底，并重置计数器。必须在使用了**StarCounterRule**并配置了相关星级的计数后，才能正常工作。<br>
包含以下配置项:

  - **star_pity**: 星级保底字典，如 `{"5": 90, "4": 10}`，表示 5 星卡片的保底阈值为 90 次，4 星卡片的保底阈值为 10 次。
  - **reset_lower_pity**: 当抽出高星级卡片时，**是否重置低星级卡片的保底计数**。这一重置操作在**回调**中完成。

  **注意**: 若两个星级同时触发保底，将**只触发**优先的星级保底。保底触发的优先级按照 **star_pity** 中的**配置顺序**规定，而**不由**星级的大小规定。


- **TypeStarPityRule**: **基于星级的类型保底规则**，提供对应星级下各类型的保底，若抽卡次数达到阈值，则触发保底，并重置计数器。必须在使用了**TypeStarCounterRule**并配置了相关星级下类型的计数后，才能正常工作。<br>
包含以下配置项:
  
  - **type_pity**: 类型保底字典，如 `{"5": {"Character": 1}, "4": {"Weapon": 1}}`，表示 5 星卡片中，角色卡片的保底阈值为 1 次；四星卡片中，武器卡片的保底阈值为 1 次。


- **UpRule**: **UP 规则**, 提供基于星级的 UP 规则，每次根据对应星级的 UP 概率决定是否为 UP，同时附带 UP 计数器和 UP 保底功能。必须**在确定当前抽星级后使用**，才能正常工作。<br>
包含以下配置项:

  - **up_probability**: UP 概率字典，如 `{"5": 1000, "4": 5000}`，表示 5 星卡片的 UP 概率为 10%，4 星卡片的 UP 概率为 50%。(相对于总权重：10000)
  - **up_pity**: UP 保底字典，如 `{"5": 1, "4": 1}`，表示 5 星卡片的 UP 保底阈值为 1 次，4 星卡片的 UP 保底阈值为 1 次。

  **注意**: UP 计数器的更新在**执行**中完成，且每次抽卡**只更新当前抽星级下**的计数器。


- **UpTypeRule**: **UP 类型分布规则**，用于在 UP 规则触发 UP 后，根据 UP 类型概率表，决定 UP 卡片的类型，同时附带基于星级的 UP 类型计数器和保底。必须**在确定当前抽星级后使用**，才能正常工作。<br>
包含以下配置项:

  - **up_type_probability**: UP 类型概率字典，如 `{"5": {"Character": 10000}, "4": {"Character": 5000, "Weapon": 5000}}`，表示 5 星卡片的 UP 类型为角色，4 星卡片的 UP 类型为角色或武器，且概率均等。
  - **up_type_pity**: UP 类型保底字典，如 `{"5": {"Character": 1}, "4": {"Character": 1}}`，表示 5 星卡片中，角色卡片的 UP 保底阈值为 1 次；四星卡片中，角色卡片的 UP 保底阈值为 1 次。


- **StarProbabilityIncreaseRule**: **星级概率增长规则**，实现星级概率从**指定抽数**开始，随抽数**等差增长**。由于原理是在每次抽卡开始前，修改 **StarProbabilityRule** 的概率，因此必须在使用了**StarCounterRule**并配置了相关星级的计数后，且先于 **StarProbabilityRule** 执行，才能正常工作。<br>
包含以下配置项:

  - **star_increase**: 星级概率增长字典，如 `{"5": [74, 600], "4": [9, 5100]}`，表示 5 星卡片的概率从第 74 次抽卡开始，每次抽卡后增加 6%，4 星卡片的概率从第 9 次抽卡开始，每次抽卡后增加 51%。

  **注意**: 该规则项的配置**不会影响**基础概率，只会影响**增长后的概率**。且当 **StarCounterRule** 的计数重置后，该规则对概率的影响也将重置。


- **StarProbabilityIntervalIncreaseRule**: **星级概率区间增长规则**，实现星级概率在**不同区间**内随抽数内**等差增长**。由于原理是在每次抽卡开始前，修改 **StarProbabilityRule** 的概率，因此必须在使用了**StarCounterRule**并配置了相关星级的计数后，且先于 **StarProbabilityRule** 执行，才能正常工作。<br>
包含以下配置项:

  - **star_increase**: 星级概率增长字典，如 `{"5": [[66, 400], [71, 800], [76, 1000]]}`，表示 5 星卡片的概率在 66-70 次抽卡内，每次抽卡增加 4%，在 71-75 次抽卡内，每次抽卡增加 8%，在 76 次抽卡及以后，每次抽卡增加 10%。

  **注意**: 该规则项的配置**不会影响**基础概率，只会影响**增长后的概率**。且当 **StarCounterRule** 的计数重置后，该规则对概率的影响也将重置。


- **FesRule**: **Fes 规则**，在 UP 内部，再次进行 **Fes 抽取**，判定是否由 UP 卡片**升为 Fes 卡片**。必须在**确定当前星级**，并**确定是否为 UP 卡片**后，才能正常工作。<br>
包含以下配置项:

  - **fes_probability**: Fes 概率字典，如 `{"5": 1000, "4": 5000}`，表示 5 星卡片的 Fes 概率为 10%，4 星卡片的 Fes 概率为 50%。(相对于总权重：10000)


- **AppointRule**: **Appoint (定轨)规则**，在 UP 内部再次指定 Appoint (定轨)卡片，当结果为 UP 且计数器超过 Appoint 阈值时，强制结果为 Appoint (定轨)卡片。一般而言，被指定为 Appoint 的卡片同时也是 UP 卡片。必须在**确定当前星级**，并**确定是否为 UP 卡片**后，才能正常工作。<br>
包含以下配置项:

  - **appoint_pity**: Appoint 阈值字典，如 `{"5": 1, "4": 1}`，表示 5 星卡片的 Appoint 阈值为 1 次，4 星卡片的 Appoint 阈值为 1 次。

  **注意**: Appoint 计数器的更新在**回调**中完成，且只要当前抽结果不为 Appoint (定轨)卡片，计数器就会自增，否则计数器重置。


- **CaptureRule**: **捕获规则**，在进行 UP 抽取前，优先进行捕获判定, 若判定成功, 则直接判定当前抽为 UP 卡片。必须在**确定当前星级**后，才能正常工作。<br>
包含以下配置项:

  - **capture_probability**: 捕获概率字典，如 `{"5": 1000, "4": 5000}`，表示 5 星卡片的捕获概率为 10%，4 星卡片的捕获概率为 50%。(相对于总权重：10000)


- **CapturePityRule**: **捕获保底规则**，当**连续指定次数**都通过 UP 保底才获得 UP 卡片时，下次获取该星级后，必定判定捕获成功，即确定为 UP 卡片。必须在**确定当前星级**后，才能正常工作。<br>
包含以下配置项:

  - **capture_pity**: 捕获保底字典，如 `{"5": 3, "4": 1}`，表示 5 星卡片的捕获保底阈值为 3 次，4 星卡片的捕获保底阈值为 1 次。
  
  **注意**: 本规则与 **CaptureRule** 相互独立，二者均可独立使用。此外，只要当前抽**不是由 UP 保底获得的 UP 卡片**，捕获保底计数器就会重置，否则计数器自增。


#### 抽卡逻辑配置示例
```json
{
    "name": "崩坏：星穹铁道-角色-UP卡池-抽卡规则",
    "rules": {
        "StarCounterRule": {
            "star_list": [
                5, 4
            ]
        },
        "StarPityRule": {
            "star_pity": {
                "5": 90,
                "4": 10
            },
            "reset_lower_pity": false
        },
        "StarProbabilityIncreaseRule": {
            "star_increase": {
                "5": [74, 600],
                "4": [9, 5100]
            }
        },
        "StarProbabilityRule": {
            "star_probability": {
                "5": 60,
                "4": 510,
                "3": 9430
            }
        },
        "UpRule": {
            "up_probability": {
                "5": 5000,
                "4": 5000
            },
            "up_pity": {
                "5": 1,
                "4": 1
            }
        },
        "UpTypeRule": {
            "up_type_probability": {
                "4": {"Character": 10000}
            },
            "up_type_pity": {}
        },
        "TypeStarProbabilityRule": {
            "type_probability": {
                "5": {"Character": 10000},
                "4": {"Character": 5000, "Weapon": 5000},
                "3": {"Weapon": 10000}
            }
        }
    }
}
```


### 4. 卡池配置
所有的卡池都在 `Data/CardPools` 目录中配置，文件名任意，但必须以 `.json` 结尾。<br>

每个 `json` 卡池配置文件代表一个卡池，每个文件需包含以下字段：

- **name**：卡池名称，且为**唯一标识符**
- **card_group**: 使用的正式卡组名称，需在 `Data/CardGroups` 目录中存在
- **logic**: 使用的抽卡逻辑名称，需在 `Data/LogicConfig` 目录中存在
- **recorder_dir**: 抽卡记录保存目录，相对于 `Wishes` 目录，推荐在 `Data/Records` 下新建目录使用。目录中将包含三个文件: `profile.json`、`details.csv` 和 `interval.csv`，分别保存**汇总记录**、**详细记录**和**卡组中最高星级的间隔抽数记录**。
- ***logic_state**: 抽卡逻辑状态，保存抽卡逻辑的状态，如保底计数器等，该字段将在新建卡池后**自动创建**，无需手动配置。

#### 卡池配置示例
```json
{
    "name": "Normal2",
    "card_group": "默认卡组2",
    "logic": "崩坏：星穹铁道-角色-UP卡池-抽卡规则",
    "recorder_dir": "Data/Records/Normal2",
    "logic_state": {
        "StarCounterRule": {
            "star_counter": {
                "5": 32,
                "4": 0
            }
        },
        "StarPityRule": {
            "is_pity": {
                "5": false,
                "4": false
            }
        },
        "UpRule": {
            "up_counter": {
                "5": 0,
                "4": 0
            },
            "is_up_pity": {
                "5": false,
                "4": true
            }
        }
    }
}
```
**注意**: `logic_state`为自动创建

---

## English

**Note**: Some of the content is translated using AI tools, and may be not accurate. For the most accurate information, please refer to the Chinese version.

`Wishes` is a **highly customizable and adaptable gacha simulator** for games.<br>
Core features include:
- Simulating gacha algorithms
- Animated drawing effects with character/item illustrations
- Gacha history recording and statistical analytics
- Customizable pool creation & card/deck management

---

#### Important Notice
Built with [Python](https://www.python.org/) `3.13` as the primary language.<br>

Currently in **core development phase** (CLI-only). Future releases will feature a GUI using [Qt6](https://www.qt.io/) and `Qt Quick`.

---

## Getting Started
Download the latest release Wishes v3.0.1 from [GitHub Release](https://github.com/GeZhe-GAZE/Wishes/releases), extract the package, and run `Wishes.exe`.<br>

Alternatively, clone the repository from [GitHub Repository](https://github.com/GeZhe-GAZE/Wishes) and run `main_command_line.py`:

```bash
python main_command_line.py
```

## Customization
The most significant feature of `Wishes v3` is its **customization capabilities**.<br>

Customize **cards**, **decks**, **gacha logic**, and **card pools** through JSON configuration files.<br>

Detailed configuration process:

### 1. Card Configuration
Card configuration files use JSON format and reside in `Data/Cards`. Filenames are arbitrary but must end with `.json`.<br>

Directory structure: **Data/Cards/< Game >/< Type >/< StarRating >/*.json**

Each JSON file represents one card and requires these fields:

- **content**: Card content name
- **game**: Game affiliation
- **type**: Card type (e.g., **Character**, **Weapon**)
- **star**: Star rating (integer)
- **attribute**: Card attribute (e.g., **Ice**, **Fire**, **Wind**)
- **title**: Card title (currently unused)
- **profession**: Profession type (e.g., **Erudition**, **Sword**, **Break**)
- **image_path**: Illustration path (relative to Wishes directory)

After adding cards, register the directory structure in `Data/Config/CardsDirConfig.json`.

#### Card Configuration Example
```json
{
    "content": "胡桃",
    "game": "Genshin",
    "star": 5,
    "type": "Character",
    "attribute": "火",
    "title": "",
    "profession": "长柄武器",
    "image_path": "Data/Images/Genshin/Character/Star5/胡桃.png"
}
```

#### Directory Structure Example
```json
{
    "Genshin": {
        "Character": [5, 4],
        "Weapon": [5, 4, 3]
    },
    "StarRail": {
        "Character": [5, 4],
        "Weapon": [5, 4, 3]
    },
    "ZZZ": {
        "Character": [5, 4],
        "Weapon": [5, 4, 3],
        "Bangboo": [5, 4]
    }
}
```

### 2. Deck Configuration
Decks are categorized as **Standard Decks** and **Formal Decks**. Standard decks are reusable components of formal decks.

#### 2.1 Standard Deck Configuration
Standard decks are configured in `Data/StandardGroups` (files must end with `.json`).

Each file requires:

- **name**: Deck name, Unique identifier
- **Type → StarRating → Card Group**: Cards must include:
  - game: Game affiliation
  - type: Card type
  - star: Star rating
  - content: Card content name

> Ensure no duplicate **content** values within the same type and star rating.

#### Standard Deck Example
```json
{
    "name": "崩坏：星穹铁道-角色-常驻-单标签卡组",
    "Character": {
        "5": [
            {
                "game": "StarRail",
                "type": "Character",
                "star": 5,
                "content": "克拉拉"
            },
            {
                "game": "StarRail",
                "type": "Character",
                "star": 5,
                "content": "姬子"
            },
            ...
        ],
        "4": [
            {
                "game": "StarRail",
                "type": "Character",
                "star": 4,
                "content": "三月七"
            },
            {
                "game": "StarRail",
                "type": "Character",
                "star": 4,
                "content": "丹恒"
            },
            ...
        ]
    },
    "Weapon": {
        "4": [
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 4,
                "content": "「我」的诞生"
            },
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 4,
                "content": "一场术后对话"
            },
            ...
        ],
        "3": [
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 3,
                "content": "乐圮"
            },
            {
                "game": "StarRail",
                "type": "Weapon",
                "star": 3,
                "content": "俱殁"
            },
            ...
        ]
    }
}
```

#### 2.2 Formal Deck Configuration
Formal decks are configured in `Data/CardGroups` (files must end with `.json`).

Each file requires:

- **name**: Unique identifier
- **version**: Pool version (currently unused)
- **is_official**: Official pool flag (currently unused)
- **standard**: Referenced standard deck name
- **exclude**: Exclusion mode (if `true`, excludes formal deck cards from standard deck)
- Additional cards categorized under **tag groups**:
  - **up**: UP cards
  - **fes**: Fes cards
  - **appoint**: Appoint (pity target) cards

> Tag groups must be **lowercase** in configuration files.

#### Formal Deck Example
```json
{
    "name": "默认卡组2",
    "version": "v3.3",
    "is_official": true,
    "standard": "崩坏：星穹铁道-角色-常驻-单标签卡组",
    "exclude": true,
    "up": {
        "Character": {
            "5": [
                {
                    "game": "StarRail",
                    "star": 5,
                    "type": "Character",
                    "content": "风堇"
                }
            ],
            "4": [
                {
                    "game": "StarRail",
                    "star": 4,
                    "type": "Character",
                    "content": "米沙"
                },
                {
                    "game": "StarRail",
                    "star": 4,
                    "type": "Character",
                    "content": "希露瓦"
                },
                {
                    "game": "StarRail",
                    "star": 4,
                    "type": "Character",
                    "content": "娜塔莎"
                }
            ]
        }
    }
}
```

### 3. Gacha Logic Configuration
Gacha logic is configured in `Data/LogicConfig` (files must end with `.json`).

Each file requires:

- **name**: Unique identifier
- **rules**: Rule chain (executed sequentially during pulls)

> Rule order matters. Rules execute during pull determination and trigger callbacks post-pull.

#### Available Rules (14)
1. **StarCounterRule**: Tracks pull counts per star rating.<br>
Config: 
  - `"star_list": [5,4,3]`

2. **TypeStarCounterRule**: Tracks pull counts per type within star ratings.<br>
Config: 
  - `"type_star_dict": {"5": ["Character", "Weapon"]}`

3. **StarProbabilityRule**: Determines star rating via weighted probabilities.<br>
Config: 
  - `"star_probability": {"5": 60, "4": 510, "3": 9430}`

  > Sum of probabilities must equal 10000. Probabilities use integer weights (e.g., 0.6% = 60).

4. **TypeStarProbabilityRule**: Determines card type given a star rating.<br>
Config: 
  -`"type_probability": {"5": {"Character": 10000}}`

5. **StarPityRule**: Implements pity counters per star rating.<br>
Config: 
  - `"star_pity": {"5": 90, "4": 10}`
  - `"reset_lower_pity: true"` (reset lower star pity counters when cards of higher star ratings are drawn)

6. **TypeStarPityRule**: Implements pity counters per type within star ratings.<br>
Config: 
  - `"type_pity": {"5": {"Character": 1}}`

7. **UpRule**: Determines UP status and implements UP pity.<br>
Config: 
  - `"up_probability": {"5": 5000}, "up_pity": {"5": 1}`
  - `"up_pity": {"5": 1, "4": 1}`

8. **UpTypeRule**: Determines UP type distribution.<br>
Config: 
  - `"up_type_probability": {"5": {"Character": 10000}}`
  - `"up_type_pity": {"5": {"Character": 1}}`

9. **StarProbabilityIncreaseRule**: Linearly increases star probability after threshold.<br>
Config: 
  - `"star_increase": {"5": [74, 600]}` (Increases 5★ probability by 6% starting at pull 74)

10. **StarProbabilityIntervalIncreaseRule**: Increases star probability in intervals.<br>
Config: 
  - `"star_increase": {"5": [[66,400],[71,800]]}`

11. **FesRule**: Determines Fes status within UP pulls.<br>
Config: 
  - `"fes_probability": {"5": 1000}`

12. **AppointRule**: Implements Appoint (pity target) mechanics.<br>
Config: 
  - `"appoint_pity": {"5": 1}`

13. **CaptureRule**: Pre-UP capture probability.<br>
Config: 
  - `"capture_probability": {"5": 1000}`

14. **CapturePityRule**: Capture pity counter.<br>
Config: 
  - `"capture_pity": {"5": 3}`

#### Gacha Logic Example
```json
{
    "name": "崩坏：星穹铁道-角色-UP卡池-抽卡规则",
    "rules": {
        "StarCounterRule": {
            "star_list": [
                5, 4
            ]
        },
        "StarPityRule": {
            "star_pity": {
                "5": 90,
                "4": 10
            },
            "reset_lower_pity": false
        },
        "StarProbabilityIncreaseRule": {
            "star_increase": {
                "5": [74, 600],
                "4": [9, 5100]
            }
        },
        "StarProbabilityRule": {
            "star_probability": {
                "5": 60,
                "4": 510,
                "3": 9430
            }
        },
        "UpRule": {
            "up_probability": {
                "5": 5000,
                "4": 5000
            },
            "up_pity": {
                "5": 1,
                "4": 1
            }
        },
        "UpTypeRule": {
            "up_type_probability": {
                "4": {"Character": 10000}
            },
            "up_type_pity": {}
        },
        "TypeStarProbabilityRule": {
            "type_probability": {
                "5": {"Character": 10000},
                "4": {"Character": 5000, "Weapon": 5000},
                "3": {"Weapon": 10000}
            }
        }
    }
}
```

### 4. Card Pool Configuration
Card pools are configured in `Data/CardPools` (files must end with `.json`).

Each file requires:

- **name**: Unique identifier
- **card_group**: Formal deck name
- **logic**: Gacha logic name
- **recorder_dir**: Pull record directory (e.g., `Data/Records/Normal2`)
- ***logic_state**: Auto-generated logic state (counters, pity status)

#### Card Pool Example
```json
{
    "name": "Normal2",
    "card_group": "默认卡组2",
    "logic": "崩坏：星穹铁道-角色-UP卡池-抽卡规则",
    "recorder_dir": "Data/Records/Normal2",
    "logic_state": {
        "StarCounterRule": {
            "star_counter": {
                "5": 32,
                "4": 0
            }
        },
        "StarPityRule": {
            "is_pity": {
                "5": false,
                "4": false
            }
        },
        "UpRule": {
            "up_counter": {
                "5": 0,
                "4": 0
            },
            "is_up_pity": {
                "5": false,
                "4": true
            }
        }
    }
}
```
**Note**: `logic_state` is auto-generated and should not be manually edited.
