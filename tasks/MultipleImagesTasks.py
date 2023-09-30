from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
from tasks.BaseTasks import *
from utils.area_utils import ch_area_rows_deviations
from abc import ABC
from utils.save_data_utils import *
import tqdm
import random
from vars import SurfaceType
from Deviations import Deviations
from scipy.stats import linregress
import vars


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
        sea = []
        snow = []
        with tqdm.tqdm(total=self.count_total_areas(), desc="Loading all areas") as pbar:
            for image in self.images:
                for area in image.selected_areas():
                    if area.get_surface_type() == SurfaceType.SEA:
                        sea.append(area)
                    elif area.get_surface_type() == SurfaceType.SNOW:
                        snow.append(area)
                    pbar.update(1)
        random.shuffle(sea)
        random.shuffle(snow)
        min_len = min(len(sea), len(snow))
        areas = sea[:min_len] + snow[:min_len]

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


class SensorsCoefficientsTask(BaseTask):
    """
    Вычисляет коэффициенты для каждого датчика и стороны зеркала
    Поля result:
        channel: Номер канала
        sensor: Номер датчика
        slope_side_1: Коэффициент наклона при первой стороне зеркала
        intercept_side_1: Коэффициент подъёма при первой стороне зеркала
        slope_side_2: Коэффициент наклона при второй стороне зеркала
        intercept_side_2: Коэффициент подъёма при второй стороне зеркала
    """
    task_name = "Вычислить коэффициенты"

    def calculate_data(self):
        year = 2023
        columns = ["channel", "sensor", "slope_side_1", "intercept_side_1", "slope_side_2", "intercept_side_2"]
        df = pd.DataFrame(columns=columns)

        with tqdm.tqdm(total=15 * 10, desc="Calculating coefficients") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    ch_sens_data = Deviations.get_dataframe(year=year, channel=channel, sensor=sensor_i)

                    filt_side_1 = ch_sens_data["k_mirror_side"] == vars.KMirrorSide.SIDE_1.value
                    filt_side_2 = ch_sens_data["k_mirror_side"] == vars.KMirrorSide.SIDE_2.value
                    side_1_data = ch_sens_data.loc[filt_side_1]
                    side_2_data = ch_sens_data.loc[filt_side_2]
                    x_side_1 = side_1_data["area_avg"].to_numpy()
                    y_side_1 = side_1_data["deviation"].to_numpy()
                    x_side_2 = side_2_data["area_avg"].to_numpy()
                    y_side_2 = side_2_data["deviation"].to_numpy()

                    linreg_side_1 = linregress(x_side_1.astype(float), y_side_1.astype(float))
                    linreg_side_2 = linregress(x_side_2.astype(float), y_side_2.astype(float))
                    slope_1 = linreg_side_1.slope
                    slope_2 = linreg_side_2.slope
                    intercept_1 = linreg_side_1.intercept
                    intercept_2 = linreg_side_2.intercept

                    significance = 0.05

                    is_slope_1_significant = linreg_side_1.pvalue < significance
                    is_slope_2_significant = linreg_side_2.pvalue < significance
                    if not is_slope_1_significant:
                        slope_1 = 0
                    if not is_slope_2_significant:
                        slope_2 = 0

                    row = [channel, sensor_i, slope_1, intercept_1, slope_2, intercept_2]
                    df.loc[len(df)] = row

                    pbar.update(1)
        df.to_pickle("cal_coeffs.pkl")
        return df


MULTI_IMAGE_TASKS = [
    MultipleImagesCalibrationTask,
    DeviationsLinearRegression,
    DeviationsBySurface,
    DeviationsByMirrorSide,
    DeviationsMeanPerImage,
    RegressByYear
]
DICT_MULTI_IMAGE_TASKS = {task.task_name: task for task in MULTI_IMAGE_TASKS}

t = SensorsCoefficientsTask()
t.run()
t.save_to_excel()