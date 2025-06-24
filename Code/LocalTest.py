from WishLogic import *
from Base import *
from ManageSystem import *


card_system = CardSystem("Data/Cards")
card_group_system = CardGroupSystem("Data/CardGroups", card_system)
card_pool_system = CardPoolSystem("Data/CardPools", card_group_system)
pool = card_pool_system.get_card_pool("Test")
pool.recorder.clear()

counter = 0
print(" Wishes v3.0 Console ".center(100, "-"))
print(pool.card_group)
print("\n", " 回车以单抽 ".center(20, "-"))
while True:
    q = input()
    if q.lower() == "q":
        print("退出".center(20, "-"))
        break
    if q.lower() == "r":
        pool.reset()
        print("卡池重置".center(20, "-"))
        continue
    print(pool.logic.probability, pool.logic.counter, pool.logic.next_up)
    result = pool.wish_one()
    counter += 1
    print(f"{counter}. ", result.get_one())
card_pool_system.end()
