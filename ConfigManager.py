import json
from dataclasses import dataclass
import os
import tasks


@dataclass
class AreaInfo:
    x: int
    y: int
    width: int
    height: int
    is_used: bool


@dataclass
class ImageInfo:
    path: str
    name: str
    areas: list[AreaInfo]
    is_used: bool


class ConfigManager:
    path: str
    draw_graphs: bool
    save_colored_images: bool
    images_dir: str
    images: list[ImageInfo]

    image_tasks: list[tasks.BaseImageTask]
    area_tasks: list[tasks.BaseAreaTask]

    def __init__(self, path: str):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.draw_graphs = data["DRAW_GRAPHS"]
        self.save_colored_images = data["SAVE_COLORED_IMAGES"]
        self.images_dir = data["IMAGES_DIR"]

        # Загружаем изображения и их области
        self.images = []
        for img_info in data["IMAGES"]:
            path = os.path.join(self.images_dir, img_info["PATH"])
            name = img_info["NAME"]
            is_img_used = img_info["IS_USED"]
            areas = []
            for area_info in img_info["AREAS"]:
                x = area_info["X"]
                y = area_info["Y"]
                width = area_info["WIDTH"]
                height = area_info["HEIGHT"]
                is_area_used = area_info["IS_USED"]
                area = AreaInfo(x, y, width, height, is_area_used)
                areas.append(area)
            img = ImageInfo(path, name, areas, is_img_used)
            self.images.append(img)

        # Загружаем методы обработки
        self.image_tasks = []
        for img_task_name in data["USED_IMAGE_TASKS"]:
            self.image_tasks.append(tasks.DICT_IMAGE_TASKS[img_task_name])
        self.area_tasks = []
        for area_task_name in data["USED_AREA_TASKS"]:
            self.area_tasks.append(tasks.DICT_AREA_TASKS[area_task_name])

    def to_dict(self) -> dict:
        d = {
            "IMAGES_DIR": self.images_dir,
            "DRAW_GRAPHS": self.draw_graphs,
            "SAVE_COLORED_IMAGES": self.save_colored_images,
            "USED_IMAGE_TASKS": [],
            "USED_AREA_TASKS": [],
            "IMAGES": [],
        }
        for img in self.images:
            img_info = {
                "PATH": img.path,
                "NAME": img.name,
                "IS_USED": img.is_used,
                "AREAS": []
            }
            for area in img.areas:
                area_info = {
                    "X": area.x,
                    "Y": area.y,
                    "WIDTH": area.width,
                    "HEIGHT": area.height,
                    "IS_USED": area.is_used,
                }
                img_info["AREAS"].append(area_info)
            d["IMAGES"].append(img_info)
        for img_task in self.image_tasks:
            d["USED_IMAGE_TASKS"].append(img_task.task_name)
        for area_task in self.area_tasks:
            d["USED_AREA_TASKS"].append(area_task.task_name)
        return d

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                self.to_dict(),
                f,
                indent=2,
                ensure_ascii=False
            )

