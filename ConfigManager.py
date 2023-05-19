import json
from dataclasses import dataclass
import os
from tasks import AreaTasks, ImageTasks, MultipleImagesTasks


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

    def add_area(self, x, y, w, h):
        area = AreaInfo(x, y, w, h, False)
        self.areas.append(area)


class ConfigManager:
    path: str
    draw_graphs: bool
    save_colored_images: bool
    images_dir: str
    images: list[ImageInfo]

    area_tasks: list[AreaTasks.BaseAreaTask]
    image_tasks: list[ImageTasks.BaseImageTask]
    multi_image_tasks: list[MultipleImagesTasks.BaseMultipleImagesTask]

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
        self.area_tasks = []
        for area_task_name in data["USED_AREA_TASKS"]:
            self.area_tasks.append(AreaTasks.DICT_AREA_TASKS[area_task_name])
        self.image_tasks = []
        for img_task_name in data["USED_IMAGE_TASKS"]:
            self.image_tasks.append(ImageTasks.DICT_IMAGE_TASKS[img_task_name])
        self.multi_image_tasks = []
        for multi_img_task_name in data["USED_MULTI_IMAGE_TASKS"]:
            self.multi_image_tasks.append(MultipleImagesTasks.DICT_MULTI_IMAGE_TASKS[multi_img_task_name])

    def to_dict(self) -> dict:
        d = {
            "IMAGES_DIR": self.images_dir,
            "DRAW_GRAPHS": self.draw_graphs,
            "SAVE_COLORED_IMAGES": self.save_colored_images,
            "USED_AREA_TASKS": [],
            "USED_IMAGE_TASKS": [],
            "USED_MULTI_IMAGE_TASKS": [],
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
                    "X": int(area.x),
                    "Y": int(area.y),
                    "WIDTH": int(area.width),
                    "HEIGHT": int(area.height),
                    "IS_USED": bool(area.is_used),
                }
                img_info["AREAS"].append(area_info)
            img_info["AREAS"].sort(key=lambda x: (x["X"], x["Y"]))
            d["IMAGES"].append(img_info)
        for area_task in self.area_tasks:
            d["USED_AREA_TASKS"].append(area_task.task_name)
        for img_task in self.image_tasks:
            d["USED_IMAGE_TASKS"].append(img_task.task_name)
        for multi_img_task in self.multi_image_tasks:
            d["USED_MULTI_IMAGE_TASKS"].append(multi_img_task.task_name)
        return d

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(
                self.to_dict(),
                f,
                indent=2,
                ensure_ascii=False
            )

    def del_area(self, img_i: int, area_i: int):
        del self.images[img_i].areas[area_i]
