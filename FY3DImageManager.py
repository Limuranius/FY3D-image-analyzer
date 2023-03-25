from FY3DImage import FY3DImage, FY3DImageArea
import json
import vars
import os
import tasks
import logging
import utils


class FY3DImageManager:
    images: list[FY3DImage]
    areas: dict[FY3DImage, list[FY3DImageArea]]
    draw_graphs: bool

    image_tasks = [
        tasks.BBTask
    ]

    area_tasks = [
        tasks.Task1,
        tasks.Task2,
        tasks.Task3,
        tasks.Task4,
        tasks.Task5,
        tasks.TaskNoise1_1,
        tasks.TaskNoise1_2,
        tasks.TaskNoise2_1,
        tasks.TaskNoise2_2,
    ]

    def __init__(self, json_path: str):
        self.images = []
        self.areas = {}
        self.load_json(json_path)

    def load_json(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.draw_graphs = data["DRAW_GRAPHS"]
        images_dir = data["IMAGES_DIR"]
        images_info = data["IMAGES"]
        look_at = data["LOOK_AT"]
        for i in look_at:
            img_info = images_info[i]
            path = os.path.join(images_dir, img_info["PATH"])
            name = img_info["NAME"]
            image = FY3DImage(path, name)
            areas_info = img_info["AREAS"]
            areas = []
            for area_info in areas_info:
                x = area_info["X"]
                y = area_info["Y"]
                width = area_info["WIDTH"]
                height = area_info["HEIGHT"]
                area = image.get_area(x, y, width, height)
                areas.append(area)
            self.images.append(image)
            self.areas[image] = areas

    def save_colored_images(self):
        logging.info(f"Сохраняем цветные изображения с областями")
        for image in self.images:
            image_areas = self.areas[image]
            colored_image = image.get_colored_picture(image_areas)
            file_name = image.name + ".png"
            file_path = os.path.join(vars.COLORED_PICTURES_PATH, file_name)
            utils.create_dirs(vars.COLORED_PICTURES_PATH)
            colored_image.save(file_path)
            logging.info(f"Изображение \"{image.name}\" сохранено")

    def analyze_images(self):
        utils.remove_dir(vars.RESULTS_DIR)
        logging.info(f"Начинаем анализ изображений.")
        for image in self.images:
            logging.info(f"Анализируем изображение\"{image.name}\"...")
            for image_task in self.image_tasks:
                image_task(image).analyze(self.draw_graphs)

            logging.info(f"Анализируем области изображения:")
            for area in self.areas[image]:
                logging.info(f"Анализируем область\"{area.name}\"...")
                for area_task in self.area_tasks:
                    area_task(area).analyze(self.draw_graphs)


