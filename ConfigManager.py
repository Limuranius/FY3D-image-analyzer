import json
from tasks import AreaTasks, ImageTasks, MultipleImagesTasks


class ConfigManager:
    path: str
    draw_graphs: bool
    save_colored_images: bool
    images_dir: str

    area_tasks: list[AreaTasks.BaseAreaTask]
    image_tasks: list[ImageTasks.BaseImageTask]
    multi_image_tasks: list[MultipleImagesTasks.BaseMultipleImagesTask]

    def __init__(self, path: str):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.draw_graphs = data["DRAW_GRAPHS"]
        self.save_colored_images = data["SAVE_COLORED_IMAGES"]

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
            "DRAW_GRAPHS": self.draw_graphs,
            "SAVE_COLORED_IMAGES": self.save_colored_images,
            "USED_AREA_TASKS": [],
            "USED_IMAGE_TASKS": [],
            "USED_MULTI_IMAGE_TASKS": [],
        }
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
