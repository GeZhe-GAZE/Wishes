from ManageSystem import WishRuleSystem

system = WishRuleSystem(r"Data/LogicConfig")
logic = system.logics["蔚蓝档案-Fes卡池-抽卡规则"]

counter = 0
while True:
    input()
    counter += 1
    res = logic.wish()
    print(f"{counter}. {res}")
    # if res.star == 5:
    #     print("-" * 50)
    #     counter = 0
    # if res.star == 4:
    #     print("+" * 50)
    if res.star == 3:
        counter = 0
        print("+" * 50)
    if res.star == 2:
        print("-" * 50)
    if res.is_up:
        print("*" * 80)
    if res.is_fes:
        print("!" * 100)
