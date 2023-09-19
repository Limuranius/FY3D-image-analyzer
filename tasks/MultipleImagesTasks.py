from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
from tasks.BaseTasks import *
from utils.area_utils import ch_area_rows_deviations
from abc import ABC
from utils.save_data_utils import *
import tqdm


class BaseMultipleImagesTask(BaseTask, ABC):
    images: list[FY3DImage]

    def __init__(self, images: list[FY3DImage]):
        super().__init__()
        self.images = images

    def count_total_areas(self) -> int:
        count = 0
        for image in self.images:
            count += image.selected_areas().count()
        return count


class MultipleImagesCalibrationTask(BaseMultipleImagesTask):
    """
    Находит калибровочные коэффициенты каждого снимка
    Поля таблицы result:
        channel:    Номер канала
        img_name:   Название снимка
        c1:         Коэффициент 1
        c2:         Коэффициент 2
        c3:         Коэффициент 3
    """

    task_name = "Калибровочные коэффициенты снимков"

    def calculate_data(self) -> pd.DataFrame:
        columns = ["channel", "img_name", "c1", "c2", "c3"]
        df = pd.DataFrame(columns=columns)
        for ch in range(5, 20):
            ch_i = ch - 5
            for image in self.images:
                coeffs = image.VIS_Cal_Coeff[ch_i].tolist()
                row = [ch, image.get_unique_name(), *coeffs]
                df.loc[len(df)] = row
        return df


class AllAreasDeviations(BaseMultipleImagesTask):
    """
    Вспомогательный метод. Высчитывает отклонения всех датчиков и другую дополнительную информацию
    Поля таблицы result:
        channel:            Канал
        name:               Название области
        area_avg:           Ср. яркость области
        sensor_i:           Номер датчика
        sensor_deviation:   Отклонение датчика в этой области
        surface_type:       Тип поверхности области
        mirror_side:        Сторона зеркала
        year:               Год снимка
    """
    task_name = "Отклонение датчиков по всем областям"

    def calculate_data(self):
        columns = ["channel", "name", "area_avg", "sensor_i", "sensor_deviation", "surface_type", "mirror_side", "year"]
        total_rows = self.count_total_areas() * 150
        df = pd.DataFrame(index=range(total_rows), columns=columns)
        curr_i = 0

        # Загружаем все области
        areas = []
        with tqdm.tqdm(total=self.count_total_areas(), desc="Loading all areas") as pbar:
            for image in self.images:
                for area in image.selected_areas():
                    areas.append(area)
                    pbar.update(1)

        # areas = FY3DImageArea.select().join(FY3DImage).where(
        #     (FY3DImageArea.is_selected == True) &
        #     (FY3DImage.is_selected == True)
        # )

        with tqdm.tqdm(total=total_rows, desc="Calculating sensors deviations in all areas") as pbar:
            for channel in range(5, 20):
                for area in areas:
                    ch_area = area.get_vis_channel(channel)
                    deviations = ch_area_rows_deviations(ch_area)
                    area_avg = ch_area.mean()
                    for sensor_i in range(0, 10):
                        sensor_deviation = deviations[sensor_i]
                        row = [channel, area.get_short_name(), area_avg, sensor_i, sensor_deviation,
                               area.get_surface_type(),
                               area.get_mirror_side(), area.image.get_year()]
                        df.loc[curr_i] = row
                        curr_i += 1
                        pbar.update(1)

        return df


class DeviationsLinearRegression(BaseMultipleImagesTask):
    """Находит отклонение каждого датчика в каждой области каждого снимка и яркость этой области"""
    task_name = "Линейная регрессия зависимости отклонения от яркости"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()


class DeviationsBySurface(BaseMultipleImagesTask):
    task_name = "Отклонения в зависимости от яркости и поверхности"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()


class DeviationsByMirrorSide(BaseMultipleImagesTask):
    task_name = "Отклонения в зависимости от яркости и зеркала"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()


class DeviationsMeanPerImage(BaseMultipleImagesTask):
    """
    На каждом снимке находятся средние яркости областей и отклонения от них
    Поля result:
        channel:    Номер канала
        img_name:   Название снимка
        sensor_i:   Номер датчика
        deviation:  Отклонение датчика от среднего по снимку
        ch_avg:     Средняя яркость снимка
    """

    task_name = "Отклонения по средним по снимку"

    def calculate_data(self):
        columns = ["channel", "img_name", "sensor_i", "deviation", "ch_avg"]
        df = pd.DataFrame(index=range(len(self.images) * 150), columns=columns)
        curr_i = 0
        for channel in range(5, 20):
            for image in self.images:
                sum_brightness = 0
                pixel_count = 0
                for area in image.selected_areas():
                    ch_area = area.get_vis_channel(channel)
                    sum_brightness += ch_area.sum()
                    pixel_count += ch_area.size
                ch_avg = sum_brightness / pixel_count
                for sensor_i in range(10):
                    sum_sens_brightness = 0
                    sens_pixel_count = 0
                    for area in image.selected_areas():
                        ch_area = area.get_vis_channel(channel)
                        sum_sens_brightness += ch_area[sensor_i].sum()
                        sens_pixel_count += ch_area[sensor_i].size
                    sensor_avg = sum_sens_brightness / sens_pixel_count
                    sensor_deviation = sensor_avg - ch_avg
                    row = [channel, image.name, sensor_i, sensor_deviation, ch_avg]
                    df.loc[curr_i] = row
                    curr_i += 1
        return df


class RegressByYear(BaseMultipleImagesTask):
    task_name = "Линии регрессии по годам"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()


MULTI_IMAGE_TASKS = [
    MultipleImagesCalibrationTask,
    DeviationsLinearRegression,
    DeviationsBySurface,
    DeviationsByMirrorSide,
    DeviationsMeanPerImage,
    RegressByYear
]
DICT_MULTI_IMAGE_TASKS = {task.task_name: task for task in MULTI_IMAGE_TASKS}
