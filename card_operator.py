from pathlib import Path
import json
import os


path = r"Data/Cards"


def process(target_dir: str):
    for game in os.listdir(target_dir):
        p = Path(os.path.join(target_dir, game))
        for file in p.rglob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            new_data = {
                "content": data["content"],
                "game": game,
                "star": data["star"],
                "type": data["type"],
                "attribute": data["attribute"],
                "title": "",
                "profession": data["profession"],
                "image_path": data["image_path"]
            }
            with open(file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, indent=4, ensure_ascii=False)



if __name__ == "__main__":
    process(path)
