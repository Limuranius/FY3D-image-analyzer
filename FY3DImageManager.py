from FY3DImage import FY3DImage, FY3DImageArea
import vars
import os
import logging
import utils
from ConfigManager import ConfigManager


class FY3DImageManager:
    images: list[FY3DImage]
    config: ConfigManager

    def __init__(self, config: ConfigManager = None):
        if config is None:
            self.config = ConfigManager(vars.CONFIG_PATH)
        else:
            self.config = config
        self.images = []

    def load_config(self):
        for img_info in self.config.images:
            if not img_info.is_used:
                continue
            image = FY3DImage(
                img_info.path,
                img_info.name
            )
            for area_info in img_info.areas:
                if not area_info.is_used:
                    continue
                image.add_area(
                    area_info.x, area_info.y,
                    area_info.width, area_info.height
                )
            self.images.append(image)

    def save_colored_images(self):
        logging.info(f"Сохраняем цветные изображения с областями")
        for image in self.images:
            colored_image = image.get_colored_picture()
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
            for image_task in self.config.image_tasks:
                image_task(image).analyze(self.config.draw_graphs)

            logging.info(f"Анализируем области изображения:")
            for area in image.areas:
                logging.info(f"Анализируем область\"{area.name}\"...")
                for area_task in self.config.area_tasks:
                    area_task(area).analyze(self.config.draw_graphs)

    def run(self):
        self.load_config()
        if self.config.save_colored_images:
            self.save_colored_images()
        self.analyze_images()
