from ManageSystem import *
from Const import *
from typing import Dict, Callable, Tuple
import os
import traceback
import sys
import colorama
from colorama import Fore, Style


PROGRAM_DIR = os.getcwd()

CARDS_DIR = os.path.join(PROGRAM_DIR, r"Data/Cards")
CARDS_DIR_CONFIG_FILE = os.path.join(PROGRAM_DIR, r"Data/Config/CardsDirConfig.json")
RESIDENT_GROUP_DIR = os.path.join(PROGRAM_DIR, r"Data/ResidentGroups")
CARD_GROUP_DIR = os.path.join(PROGRAM_DIR, r"Data/CardGroups")
LOGIC_CONFIG_DIR =os.path.join(PROGRAM_DIR, r"Data/LogicConfig")
CARD_POOL_DIR = os.path.join(PROGRAM_DIR, r"Data/CardPools")


start_message = f"""
-------------------------------------------------------------
Wishes {VERSION}    Author: GeZhe-GAZE (歌者GAZE)
A highly customizable and adaptable gacha simulator for games

Welcome to use!
Type "help" for more information.


这是一个高度自定义、高度适配性的模拟游戏抽卡工具

欢迎使用！
输入 "help" 获取更多信息。
-------------------------------------------------------------
"""


class Program:
    def __init__(self):
        # 初始化 colorama
        colorama.init()

        try:
            with open(CARDS_DIR_CONFIG_FILE, "r", encoding="utf-8") as f:
                cards_dir_config = json.load(f)

            # 初始化管理系统
            self.card_system = CardSystem(CARDS_DIR, cards_dir_config)
            self.resident_group_system = ResidentGroupSystem(RESIDENT_GROUP_DIR, self.card_system)
            self.card_group_system = CardGroupSystem(CARD_GROUP_DIR, self.card_system, self.resident_group_system)
            self.wish_logic_system = WishLogicSystem(LOGIC_CONFIG_DIR)
            self.card_pool_system = CardPoolSystem(CARD_POOL_DIR, self.card_group_system, self.wish_logic_system)
        except:
            print(Fore.RED + "Initialization Error: " + traceback.format_exc())
            print("Error initializing the program. Please check the configuration files.  初始化程序错误，请检查配置文件。")
            input("Press Enter to exit.  按回车键退出。" + Style.RESET_ALL)
            sys.exit(1)

        self.commands: Dict[str, Tuple[Callable, Tuple, str, str]] = {
            "help": (self.help, (), "Show help information", "显示帮助信息"),
            "quit": (self.quit, (), "Quit the program", "退出程序"),
            "cps": (self.cps, (), "Show all card pools", "显示所有卡池"),
            "cgs": (self.cgs, (), "Show all card groups", "显示所有卡组"),
            "logics": (self.logics, (), "Show all wish logics", "显示所有抽卡逻辑"),
            "switch": (self.switch, ("card_pool_name",), "Switch to the specified card pool", "切换到指定卡池"),
            "cgroup": (self.cgroup, (), "Show the current card group", "显示当前卡组"),
            "wish": (self.wish, (), "Wish once", "抽一次"),
            "wishten": (self.wishten, (), "Wish ten times", "抽十次"),
            "wishcount": (self.wishcount, ("count",), "Wish the specified number of times", "抽指定次数"),
            "save": (self.save, (), "Save the current card pool", "保存当前卡池"),
            "reset": (self.reset, (), "Reset the current card pool", "重置当前卡池"),
        }

        # self.commands_docs: Dict[str, Tuple[Tuple, str, str]] = {
        #     "help": ((), "Show help information", "显示帮助信息"),
        #     "quit": ((), "Quit the program", "退出程序"),
        #     "cps": ((), "Show all card pools", "显示所有卡池"),
        #     "cgs": ((), "Show all card groups", "显示所有卡组"),
        #     "logics": ((), "Show all wish logics", "显示所有抽卡逻辑"),
        #     "switch": (("card_pool_name",), "Switch to the specified card pool", "切换到指定卡池"),
        #     "cgroup": ((), "Show the current card group", "显示当前卡组"),
        #     "wish": ((), "Wish once", "抽一次"),
        #     "wishten": ((), "Wish ten times", "抽十次"),
        #     "wishcount": (("count",), "Wish the specified number of times", "抽指定次数"),
        #     "save": ((), "Save the current card pool", "保存当前卡池"),
        #     "reset": ((), "Reset the current card pool", "重置当前卡池"),
        # }

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

            func = self.commands.get(command, (None,))[0]
            if not func:
                self.report_error(f"Invalid command 无效命令: <{command}>")
                continue

            parameters = self.commands[command][1]
            if len(messages) - 1 != len(parameters):
                self.report_error(f"Invalid parameters 无效参数: <{command} ({' '.join(parameters)})>")
                continue

            try:
                func(*messages[1:])
            except Exception:
                self.report_error(traceback.format_exc())
    
    def report_error(self, error_message: str):
        print(Fore.RED + f"Error: {error_message}" + Style.RESET_ALL)

    def help(self):
        max_command_name_length = max(len(command) for command in self.commands.keys())

        max_command_length = max(
            max_command_name_length + len(" ".join(parameters)) + 3    # +3 是括号和空格的长度
            for (_, parameters, _, _) in self.commands.values()
        )

        max_english_doc_length = max(len(english_doc) for (_, _, english_doc, _) in self.commands.values())

        print("-" * 20 + "\nAll commands 所有命令: \n")
        for command, info in self.commands.items():
            _, parameters, english_doc, chinese_doc = info
            command_part = f"{command:<{max_command_name_length}}" + f" ({' '.join(parameters)})"
            print(f"{command_part:<{max_command_length}} - {english_doc:<{max_english_doc_length}}  {chinese_doc}")
        print("-" * 20)

    def quit(self):
        while True:
            if self.current_card_pool and not self.is_saved:
                m = input(Fore.YELLOW + "Do you want to save the current card pool first?  你想要先保存当前卡池吗？(Y/N): " + Style.RESET_ALL)
                if m.lower() == "y":
                    self.save()
                elif m.lower() != "n":
                    continue
            break

        print("Program exited  程序已退出")
        sys.exit(0)

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
        counter = 1
        max_number_length = len(str(len(self.wish_logic_system.logics)))
        for logic_name in self.wish_logic_system.get_logic_names():
            print(f"{counter:>{max_number_length}}. {logic_name}")
            counter += 1
        print("-" * 20)

    def switch(self, card_pool_name: str):
        if card_pool_name not in self.card_pool_system.get_card_pool_names():
            self.report_error(f"The card pool does not exist  该卡池不存在: <{card_pool_name}>")
            return
        if not self.is_saved:
            while True:
                m = input(Fore.YELLOW + "Do you want to save the current card pool first?  你想要先保存原先卡池吗？(Y/N): " + Style.RESET_ALL)
                if m.lower() == "y":
                    self.save()
                elif m.lower() != "n":
                    continue
                break
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
        print(Fore.BLUE + f"{self.counter}. {packed_card}" + Style.RESET_ALL)

        self.is_saved = False

    def wishten(self):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        
        result = self.current_card_pool.wish_ten()
        for packed_card in result.cards:
            self.counter += 1
            print(Fore.BLUE + f"{self.counter}. {packed_card}" + Style.RESET_ALL)

        self.is_saved = False
    
    def wishcount(self, count_s: str):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        
        count = int(count_s)
        if count <= 0:
            self.report_error("Invalid count 无效次数: <{count}>")
        if count >= 10000:
            while True:
                m = input(Fore.YELLOW + "Warning: The count is too large, do you want to continue?  次数过大，你想要继续吗？(Y/N) " + Style.RESET_ALL)
                if m.lower() == "y":
                    print("Wishing...  抽卡中...")
                    break
                elif m.lower() != "n":
                    continue
                return

        result = self.current_card_pool.wish_count(count)
        print("Wishing is completed, waiting for output...  抽卡已完成，等待输出...")
        for packed_card in result.cards:
            self.counter += 1
            print(Fore.BLUE + f"{self.counter}. {packed_card}" + Style.RESET_ALL)

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
    
    def reset(self):
        if not self.current_card_pool:
            self.report_error("No card pool is currently selected  当前没有选择卡池")
            return
        while True:
            m = input(Fore.YELLOW + "Are you sure you want to reset the current card pool?  你想要重置当前卡池吗？(Y/N) " + Style.RESET_ALL)
            if m.lower() == "y":
                break
            elif m.lower() != "n":
                continue
            return
        while True:
            m = input(Fore.YELLOW +"And do you want to clear the records at the same time?  你想要同时清空记录吗？(Y/N) " + Style.RESET_ALL)
            if m.lower() == "y":
                with_records = True
                break
            elif m.lower() != "n":
                continue
            with_records = False
            break
        self.current_card_pool.reset(with_records)
        self.counter = 0
        self.is_saved = False
        print(f"Card pool reset  卡池已重置: <{self.current_card_pool.name}>")
        if with_records:
            print("Records cleared  记录已清空")


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
