from ManageSystem import *


CARDS_DIR = r"Data/Cards"
CARDS_DIR_CONFIG_FILE = r"Data/Config/CardsDirConfig.json"
RESIDENT_GROUP_DIR = r"Data/ResidentGroups"
CARD_GROUP_DIR = r"Data/CardGroups"
LOGIC_CONFIG_DIR = r"Data/LogicConfig"
CARD_POOL_DIR = r"Data/CardPools"

CARD_POOL_FILE = r"Data/CardPools/Test.json"


def main():
    with open(CARDS_DIR_CONFIG_FILE, "r", encoding="utf-8") as f:
        cards_dir_config = json.load(f)

    # 初始化管理系统
    card_system = CardSystem(CARDS_DIR, cards_dir_config)
    resident_group_system = ResidentGroupSystem(RESIDENT_GROUP_DIR, card_system)
    card_group_system = CardGroupSystem(CARD_GROUP_DIR, card_system, resident_group_system)
    wish_logic_system = WishLogicSystem(LOGIC_CONFIG_DIR)
    card_pool_system = CardPoolSystem(CARD_POOL_DIR, card_group_system, wish_logic_system)

    card_pool = card_pool_system.get_card_pool("Test")
    print(card_pool.card_group)
    
    counter = 0

    while True:
        counter += 1
        command = input()
        if command == "q":
            break

        result = card_pool.wish_one()
        packed_card = result.get_one()

        print(f"{counter}. {packed_card}")
        card = packed_card.card
        if card.star == card_pool.card_group.max_star:
            print("*" * 50)
            if packed_card.tag == TAG_UP:
                print("*" * 100)
        if card.star == card_pool.card_group.max_star - 1:
            print("-" * 50)



    card_pool_system.save_card_pool("Test", CARD_POOL_FILE)

if __name__ == "__main__":
    main()
