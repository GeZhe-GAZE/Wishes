from ManageSystem import *
from Const import *
from typing import Dict, Callable, Tuple
import os


CARDS_DIR = r"Data/Cards"
CARDS_DIR_CONFIG_FILE = r"Data/Config/CardsDirConfig.json"
RESIDENT_GROUP_DIR = r"Data/ResidentGroups"
CARD_GROUP_DIR = r"Data/CardGroups"
LOGIC_CONFIG_DIR = r"Data/LogicConfig"
CARD_POOL_DIR = r"Data/CardPools"


start_message = f"""
-------------------------------------------------------------
Wishes {VERSION}    Author: GeZhe-GAZE
A highly customizable and adaptable gacha simulator for games

Welcome to use!
Type "help" to get more information.


这是一个高度自定义、高度适配性的模拟游戏抽卡工具

欢迎使用！
输入 "help" 获取更多信息。
-------------------------------------------------------------
"""


class Program:
    def __init__(self):
        with open(CARDS_DIR_CONFIG_FILE, "r", encoding="utf-8") as f:
            cards_dir_config = json.load(f)

        # 初始化管理系统
        self.card_system = CardSystem(CARDS_DIR, cards_dir_config)
        self.resident_group_system = ResidentGroupSystem(RESIDENT_GROUP_DIR, self.card_system)
        self.card_group_system = CardGroupSystem(CARD_GROUP_DIR, self.card_system, self.resident_group_system)
        self.wish_logic_system = WishLogicSystem(LOGIC_CONFIG_DIR)
        self.card_pool_system = CardPoolSystem(CARD_POOL_DIR, self.card_group_system, self.wish_logic_system)

        self.commands: Dict[str, Callable] = {
            "help": self.help,
            "quit": self.quit,
            "cps": self.cps,
            "cgs": self.cgs,
            "logics": self.logics,
            "switch": self.switch,
            "cgroup": self.cgroup,
            "wish": self.wish,
            "wishten": self.wishten,
            "wishcount": self.wishcount,
            "save": self.save,
        }

        self.commands_docs: Dict[str, Tuple[Tuple, str, str]] = {
            "help": ((), "Show help information", "显示帮助信息"),
            "quit": ((), "Quit the program", "退出程序"),
            "cps": ((), "Show all card pools", "显示所有卡池"),
            "cgs": ((), "Show all card groups", "显示所有卡组"),
            "logics": ((), "Show all wish logics", "显示所有抽卡逻辑"),
            "switch": (("card_pool_name",), "Switch to the specified card pool", "切换到指定卡池"),
            "cgroup": ((), "Show the current card group", "显示当前卡组"),
            "wish": ((), "Wish once", "抽一次"),
            "wishten": ((), "Wish ten times", "抽十次"),
            "wishcount": (("count",), "Wish the specified number of times", "抽指定次数"),
            "save": ((), "Save the current card pool", "保存当前卡池"),
        }

        self.current_card_pool: CardPool | None = None
        self.is_saved = True
        self.counter = 0

    def mainloop(self):
        print(start_message)

        while True:
            messages = input(">>> ").split()
            if not messages:
                continue

            command = messages[0]

            func = self.commands.get(command)
            if not func:
                self.report_error(f"Invalid command 无效命令: <{command}>")
                continue

            parameters = self.commands_docs[command][0]
            if len(messages) - 1 != len(parameters):
                self.report_error(f"Invalid parameters 无效参数: <{command} ({' '.join(parameters)})>")
                continue

            try:
                func(*messages[1:])
            except Exception as e:
                self.report_error(str(e))
    
    def report_error(self, error_message: str):
        print(f"\033[31mError: {error_message}\033[0m")

    def help(self):
        max_command_name_length = max(len(command) for command in self.commands_docs)

        max_command_length = max(
            max_command_name_length + len(" ".join(parameters)) + 3    # +3 是括号和空格的长度
            for (parameters, _, _) in self.commands_docs.values()
        )

        max_english_doc_length = max(len(english_doc) for (_, english_doc, _) in self.commands_docs.values())

        print("-" * 20 + "\nAll commands 所有命令: \n")
        for command, info in self.commands_docs.items():
            parameters, english_doc, chinese_doc = info
            command_part = f"{command:<{max_command_name_length}}" + f" ({' '.join(parameters)})"
            print(f"{command_part:<{max_command_length}} - {english_doc:<{max_english_doc_length}}  {chinese_doc}")
        print("-" * 20)

    def quit(self):
        while True:
            if self.current_card_pool and not self.is_saved:
                m = input("\033[33mDo you want to save the current card pool first?  你想要先保存当前卡池吗？(Y/N): \033[0m")
                if m.lower() == "y":
                    self.save()
                elif m.lower() != "n":
                    continue
            break

        print("Program exited  程序已退出")
        exit(0)

    def cps(self):
        print("-" * 20 + "\nAll card pools 所有卡池: \n")
        for card_pool_name in self.card_pool_system.get_card_pool_names():
            print(card_pool_name)
        print("-" * 20)
    
    def cgs(self):
        print("-" * 20 + "\nAll card groups 所有卡组: \n")
        for card_group_name in self.card_group_system.get_card_group_names():
            print(card_group_name)
        print("-" * 20)
    
    def logics(self):
        print("-" * 20 + "\nAll wish logics 所有抽卡逻辑: \n")
        for logic_name in self.wish_logic_system.get_logic_names():
            print(logic_name)
        print("-" * 20)

    def switch(self, card_pool_name: str):
        if card_pool_name not in self.card_pool_system.get_card_pool_names():
            self.report_error(f"The card pool does not exist  该卡池不存在: <{card_pool_name}>")
            return
        self.current_card_pool = self.card_pool_system.get_card_pool(card_pool_name)
        print(f"Switched to the card pool  已切换到卡池: <{card_pool_name}>")
    
    def cgroup(self):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        print("-" * 20 + "\nCurrent card group 当前卡组: \n")
        print(self.current_card_pool.card_group)
        print("-" * 20)
    
    def wish(self):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        
        self.counter += 1
        result = self.current_card_pool.wish_one()
        packed_card = result.get_one()
        print(f"\033[34m{self.counter}. {packed_card}\033[0m")

        self.is_saved = False

    def wishten(self):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        
        result = self.current_card_pool.wish_ten()
        for packed_card in result.cards:
            self.counter += 1
            print(f"\033[34m{self.counter}. {packed_card}\033[0m")

        self.is_saved = False
    
    def wishcount(self, count_s: str):
        count = int(count_s)
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return

        result = self.current_card_pool.wish_count(count)
        for packed_card in result.cards:
            self.counter += 1
            print(f"\033[34m{self.counter}. {packed_card}\033[0m")

        self.is_saved = False

    def save(self):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        self.card_pool_system.save_card_pool(
            self.current_card_pool.name,
            os.path.join(CARD_POOL_DIR, self.current_card_pool.name + ".json")
        )

        self.is_saved = True
        print(f"Card pool saved  卡池已保存: <{self.current_card_pool.name}>")


def main():
    program = Program()
    program.mainloop()
    # with open(CARDS_DIR_CONFIG_FILE, "r", encoding="utf-8") as f:
    #     cards_dir_config = json.load(f)

    # # 初始化管理系统
    # card_system = CardSystem(CARDS_DIR, cards_dir_config)
    # resident_group_system = ResidentGroupSystem(RESIDENT_GROUP_DIR, card_system)
    # card_group_system = CardGroupSystem(CARD_GROUP_DIR, card_system, resident_group_system)
    # wish_logic_system = WishLogicSystem(LOGIC_CONFIG_DIR)
    # card_pool_system = CardPoolSystem(CARD_POOL_DIR, card_group_system, wish_logic_system)

    # card_pool = card_pool_system.get_card_pool("Test")
    
    # counter = 0

    # print(start_message)

    # while True:
    #     counter += 1
    #     messages = input(">>> ").split()
    #     if not messages:
    #         continue

    #     command = messages[0]

    #     if command == "q":
    #         break

    #     func = commands.get(command)
    #     if not func:
    #         print(f"Error: Invalid command 无效命令: <{command}>")
    #         continue
    #     func(*messages[1:])

        # result = card_pool.wish_one()
        # packed_card = result.get_one()

        # print(f"{counter}. {packed_card}")
        # card = packed_card.card
        # if card.star == card_pool.card_group.max_star:
        #     print("*" * 50)
        #     if packed_card.tag == TAG_UP:
        #         print("*" * 100)
        # if card.star == card_pool.card_group.max_star - 1:
        #     print("-" * 50)



    # card_pool_system.save_card_pool("Test", CARD_POOL_FILE)

if __name__ == "__main__":
    main()
