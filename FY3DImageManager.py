from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
import vars
import os
import logging
from utils import some_utils
from utils import area_utils
from ConfigManager import ConfigManager
import tqdm


class FY3DImageManager:
    images: list[FY3DImage]
    config: ConfigManager

    def __init__(self, config: ConfigManager = None):
        if config is None:
            self.config = ConfigManager(vars.CONFIG_PATH)
        else:
            self.config = config
        self.images = []

    def load(self):
        self.__calculate_std_maps()
        self.__determine_areas_surfaces()
        self.images = list(FY3DImage.select().where(FY3DImage.is_selected == True))

    def __calculate_std_maps(self):
        uncalculated_images = FY3DImage.select().where(FY3DImage.is_std_map_calculated == False)
        for img in tqdm.tqdm(uncalculated_images, desc="Calculating std maps"):
            img.calculate_std_map()

    def __determine_areas_surfaces(self):
        undetermined_areas = FY3DImageArea.select().where(FY3DImageArea.surface_type == vars.SurfaceType.UNKNOWN.value)
        for area in tqdm.tqdm(undetermined_areas, desc="Determining areas surface types"):
            surface_type = area_utils.determine_surface_type(area)
            area.surface_type = surface_type.value
            area.save()

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
        self.load()
        if self.config.save_colored_images:
            self.save_colored_images()
        self.analyze_images()
