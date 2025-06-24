import json
import os

res_dir = "Data/ResidentGroup"
file = "GenshinRole.json"
game = "Genshin"

cards_dir = f"Data/Cards/{game}/"

if file in os.listdir(res_dir):
    with open(f"{res_dir}/{file}", "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "Role": {
            "Star5": [],
            "Star4": []
        },
        "Weapon": {
            "Star5": [],
            "Star4": [],
            "Star3": []
        }
    }

excludes = [("Role", "Star5"), ("Role", "Star3")]

for type_ in ("Role", "Weapon"):
    for star in ("Star5", "Star4", "Star3"):
        if (type_, star) in excludes: continue
        cur_dir = cards_dir + f"{type_}/{star}/"
        data[type_][star] = [filename.rstrip(".json") for filename in os.listdir(cur_dir)]
        
with open(f"{res_dir}/{file}", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
