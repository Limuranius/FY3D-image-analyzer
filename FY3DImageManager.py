from FY3DImage import FY3DImage
import vars
import os
import logging
from utils import utils
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

    def load_images(self):
        self.__calculate_std_maps()
        self.images = list(FY3DImage.select().where(FY3DImage.is_selected == True))

    def __calculate_std_maps(self):
        all_images = FY3DImage.select()
        for img in all_images:
            if not img.is_std_map_calculated:
                img.calculate_std_map()

    def save_colored_images(self):
        logging.info(f"Сохраняем цветные изображения с областями")
        utils.remove_dir(vars.COLORED_PICTURES_PATH)
        utils.create_dir(vars.COLORED_PICTURES_PATH)
        for image in self.images:
            colored_image = image.get_colored_picture()
            file_name = image.name + ".png"
            file_path = os.path.join(vars.COLORED_PICTURES_PATH, file_name)
            utils.create_dir(vars.COLORED_PICTURES_PATH)
            colored_image.save(file_path)
            logging.info(f"Изображение \"{image.name}\" сохранено")

    def analyze_images(self):
        utils.remove_dir(vars.RESULTS_DIR)
        logging.info(f"Начинаем анализ изображений.")
        for image in self.images:
            logging.info(f"Анализируем изображение\"{image.name}\"...")
            for image_task in self.config.image_tasks:
                image_task(image).run(self.config.draw_graphs)

            logging.info(f"Анализируем области изображения:")
            for area in image.areas:
                logging.info(f"Анализируем область\"{area.name}\"...")
                for area_task in self.config.area_tasks:
                    area_task(area).run(self.config.draw_graphs)

        for multi_image_task in self.config.multi_image_tasks:
            multi_image_task(self.images).run(self.config.draw_graphs)

    def run(self):
        self.load_images()
        if self.config.save_colored_images:
            self.save_colored_images()
        self.analyze_images()
