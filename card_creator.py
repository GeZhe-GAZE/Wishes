import json
from Code.Const import *


game = GAME_STAR_RAIL
contents = [""]
type_ = TYPE_ROLE
star = 5
star_format = f"Star{star}"
attribute = "冰"
title = ""
profession = "存护"

for content in contents:
    file = f"Data/Cards/{game}/{type_}/{star_format}/{content}.json"
    image = f"Data/Images/{game}/{type_}/{star_format}/{content}.png"

    data = {
        "content": content,
        "star": star,
        "type": type_,
        "attribute": attribute,
        "title": title,
        "profession": profession,
        "image_path": image,
    }

    with open(file, "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
