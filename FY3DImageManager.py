from database import FY3DImage
from database import FY3DImageArea
from database import Deviations
from database import AreaStats
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
        self.__precalculate_areas()
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

    def __precalculate_areas(self):
        uncalculated_areas = FY3DImageArea.select().where(
            FY3DImageArea.is_precalculated == False)
        deviations_insert = []
        area_stats_insert = []
        for area in tqdm.tqdm(uncalculated_areas, desc="Precalculating areas"):
            for channel in range(5, 20):
                ch_area = area.get_vis_channel(channel)
                area_avg = ch_area.mean()
                deviations = area_utils.ch_area_rows_deviations(ch_area)
                for sensor_i in range(0, 10):
                    sensor_deviation = deviations[sensor_i]
                    sensor_avg = ch_area[sensor_i].mean()
                    deviations_insert.append({
                        "area": area,
                        "channel": channel,
                        "sensor": sensor_i,
                        "deviation": sensor_deviation,
                        "sensor_avg": sensor_avg
                    })
                area_stats_insert.append({
                    "area": area,
                    "channel": channel,
                    "area_avg": area_avg,
                    "area_std": ch_area.std()
                })
        FY3DImageArea.update(is_precalculated=True).where(FY3DImageArea.is_precalculated == False) \
            .execute()
        for i in tqdm.tqdm(range(0, len(deviations_insert), 999), desc="Saving deviations"):
            Deviations.insert_many(
                deviations_insert[i: i + 999]
            ).execute()
        for i in tqdm.tqdm(range(0, len(area_stats_insert), 999), desc="Saving area stats"):
            AreaStats.insert_many(
                area_stats_insert[i: i + 999]
            ).execute()

    def save_colored_images(self):
        logging.info(f"Сохраняем цветные изображения с областями")
        some_utils.remove_dir(vars.COLORED_PICTURES_PATH)
        some_utils.create_dir(vars.COLORED_PICTURES_PATH)
        for image in self.images:
            colored_image = image.get_colored_picture()
            file_name = image.name + ".png"
            file_path = os.path.join(vars.COLORED_PICTURES_PATH, file_name)
            some_utils.create_dir(vars.COLORED_PICTURES_PATH)
            colored_image.save(file_path)
            logging.info(f"Изображение \"{image.name}\" сохранено")

    def analyze_images(self):
        some_utils.remove_dir(vars.RESULTS_DIR)
        os.mkdir(vars.RESULTS_DIR)
        for image in tqdm.tqdm(self.images, desc="Running image and area tasks on images", unit="img"):
            for image_task in self.config.image_tasks:
                task = image_task(image)
                task.run()
                if self.config.draw_graphs:
                    task.save_to_graphs()
                task.save_to_excel()

            for area in image.areas:
                for area_task in self.config.area_tasks:
                    task = area_task(area)
                    task.run()
                    if self.config.draw_graphs:
                        task.save_to_graphs()
                    task.save_to_excel()

        for multi_image_task in self.config.multi_image_tasks:
            task = multi_image_task(self.images)

            if self.config.draw_graphs:
                task.save_to_graphs()
            task.save_to_excel()

        for database_task in self.config.database_tasks:
            task = database_task()
            task.save_to_excel()
            task.save_to_graphs()

    def run(self):
        self.load()
        if self.config.save_colored_images:
            self.save_colored_images()
        self.analyze_images()
