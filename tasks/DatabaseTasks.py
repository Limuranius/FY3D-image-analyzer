import pandas as pd
from time import time
import random
from tasks.BaseTasks import *
from utils.save_data_utils import *
from utils import some_utils
import tqdm
from tqdm import trange
from database import Deviations, AreaStats, FY3DImage, FY3DImageArea
from scipy.stats import linregress
from vars import KMirrorSide, SurfaceType
import vars
import os


class SensorsCoefficientsTaskByMirror(BaseTask):
    """
    Вычисляет коэффициенты для каждого датчика и стороны зеркала
    Поля result:
        channel:            Номер канала
        sensor:             Номер датчика
        slope:              Коэффициент наклона
        intercept:          Коэффициент подъёма
        k_mirror_side:      Сторона зеркала
        r^2:                Коэффициент детерминации
        pvalue:             p-значение
        slope_stderr:       Ст. ошибка коэффициента наклона
        intercept_stderr:   Ст. ошибка коэффициента подъёма
        avg_deviation:      Среднее значение отклонений
        std_deviation:      Ст. отклонение отклонений
    """
    task_name = "Вычислить коэффициенты (Сторона зеркала)"

    def calculate_data(self):
        columns = ["channel", "sensor", "slope", "intercept", "k_mirror_side",
                   "r^2", "pvalue", "slope_stderr", "intercept_stderr", "avg_deviation", "std_deviation"]
        df = pd.DataFrame(columns=columns)

        with tqdm.tqdm(total=15 * 10, desc="Calculating coefficients") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    side_1_data = Deviations.get_dataframe(channel=channel, sensor=sensor_i,
                                                           k_mirror_side=KMirrorSide.SIDE_1)
                    side_2_data = Deviations.get_dataframe(channel=channel, sensor=sensor_i,
                                                           k_mirror_side=KMirrorSide.SIDE_2)
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

                    df.loc[len(df)] = [channel, sensor_i, slope_1, intercept_1, KMirrorSide.SIDE_1.value,
                                       linreg_side_1.rvalue ** 2, linreg_side_1.pvalue, linreg_side_1.stderr,
                                       linreg_side_1.intercept_stderr, y_side_1.mean(), y_side_1.std()]
                    df.loc[len(df)] = [channel, sensor_i, slope_2, intercept_2, KMirrorSide.SIDE_2.value,
                                       linreg_side_2.rvalue ** 2, linreg_side_2.pvalue, linreg_side_2.stderr,
                                       linreg_side_2.intercept_stderr, y_side_2.mean(), y_side_2.std()]
                    pbar.update(1)
        df.to_pickle(os.path.join(vars.RESULTS_DIR, "cal_coeffs.pkl"))
        self.result = df


class SensorsCoefficientsTaskBySurface(BaseTask):
    """
    Вычисляет коэффициенты для каждого датчика и стороны зеркала
    Поля result:
        channel:            Номер канала
        sensor:             Номер датчика
        slope:              Коэффициент наклона
        intercept:          Коэффициент подъёма
        surface_type:       Тип поверхности
        r^2:                Коэффициент детерминации
        pvalue:             p-значение
        slope_stderr:       Ст. ошибка коэффициента наклона
        intercept_stderr:   Ст. ошибка коэффициента подъёма
        avg_deviation:      Среднее значение отклонений
        std_deviation:      Ст. отклонение отклонений
    """
    task_name = "Вычислить коэффициенты (тип поверхности)"

    def calculate_data(self):
        columns = ["channel", "sensor", "slope", "intercept", "surface_type",
                   "r^2", "pvalue", "slope_stderr", "intercept_stderr", "avg_deviation", "std_deviation"]
        df = pd.DataFrame(columns=columns)

        with tqdm.tqdm(total=15 * 10, desc="Calculating coefficients") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    sea = Deviations.get_dataframe(channel=channel, sensor=sensor_i,
                                                   surface_type=SurfaceType.SEA)
                    ice = Deviations.get_dataframe(channel=channel, sensor=sensor_i,
                                                   surface_type=SurfaceType.SNOW)
                    x_sea = sea["area_avg"].to_numpy()
                    y_sea = sea["deviation"].to_numpy()
                    x_ice = ice["area_avg"].to_numpy()
                    y_ice = ice["deviation"].to_numpy()

                    linreg_sea = linregress(x_sea.astype(float), y_sea.astype(float))
                    linreg_ice = linregress(x_ice.astype(float), y_ice.astype(float))
                    slope_1 = linreg_sea.slope
                    slope_2 = linreg_ice.slope
                    intercept_1 = linreg_sea.intercept
                    intercept_2 = linreg_ice.intercept

                    significance = 0.05

                    is_slope_1_significant = linreg_sea.pvalue < significance
                    is_slope_2_significant = linreg_ice.pvalue < significance
                    if not is_slope_1_significant:
                        slope_1 = 0
                    if not is_slope_2_significant:
                        slope_2 = 0

                    df.loc[len(df)] = [channel, sensor_i, slope_1, intercept_1, KMirrorSide.SIDE_1.value,
                                       linreg_sea.rvalue ** 2, linreg_sea.pvalue, linreg_sea.stderr,
                                       linreg_sea.intercept_stderr, y_sea.mean(), y_sea.std()]
                    df.loc[len(df)] = [channel, sensor_i, slope_2, intercept_2, KMirrorSide.SIDE_2.value,
                                       linreg_ice.rvalue ** 2, linreg_ice.pvalue, linreg_ice.stderr,
                                       linreg_ice.intercept_stderr, y_ice.mean(), y_ice.std()]
                    pbar.update(1)
        df.to_pickle(os.path.join(vars.RESULTS_DIR, "cal_coeffs.pkl"))
        self.result = df


class SensorsCoefficientsTask(BaseTask):
    """
    Вычисляет коэффициенты для каждого датчика
    Поля result:
        channel:            Номер канала
        sensor:             Номер датчика
        slope:              Коэффициент наклона
        intercept:          Коэффициент подъёма
        surface_type:       Тип поверхности
        r^2:                Коэффициент детерминации
        pvalue:             p-значение
        slope_stderr:       Ст. ошибка коэффициента наклона
        intercept_stderr:   Ст. ошибка коэффициента подъёма
        avg_deviation:      Среднее значение отклонений
        std_deviation:      Ст. отклонение отклонений
    """
    task_name = "Вычислить коэффициенты"

    def calculate_data(self):
        columns = ["channel", "sensor", "slope", "intercept", "surface_type",
                   "r^2", "pvalue", "slope_stderr", "intercept_stderr", "avg_deviation", "std_deviation"]
        df = pd.DataFrame(columns=columns)

        with tqdm.tqdm(total=15 * 10, desc="Calculating coefficients") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    deviations = Deviations.get_dataframe(channel=channel, sensor=sensor_i)
                    x = deviations["area_avg"].to_numpy()
                    y = deviations["deviation"].to_numpy()

                    linreg = linregress(x.astype(float), y.astype(float))
                    slope = linreg.slope
                    intercept = linreg.intercept

                    significance = 0.05

                    is_slope_significant = linreg.pvalue < significance
                    if not is_slope_significant:
                        slope = 0

                    df.loc[len(df)] = [channel, sensor_i, slope, intercept, KMirrorSide.SIDE_2.value,
                                       linreg.rvalue ** 2, linreg.pvalue, linreg.stderr,
                                       linreg.intercept_stderr, y.mean(), y.std()]
                    pbar.update(1)
        df.to_pickle(os.path.join(vars.RESULTS_DIR, "cal_coeffs.pkl"))
        self.result = df


class AreaAvgStdTask(BaseTask):
    """
    Вычисление зависимости ст. отклонения областей от их яркости
    Поля result:
        channel:    Номер канала
        area_avg:   Средняя яркость области
        area_std:   Ст. отклонение области
    """
    task_name = "Зависимость яркости области и std"

    def calculate_data(self):
        self.result = AreaStats.get_dataframe()


class DeviationsBySurface(BaseTask):
    task_name = "Отклонения в зависимости от яркости и поверхности"

    CONVERT_TO_REF = False
    SUBTRACT_BB = False

    def calculate_data(self):
        data = Deviations.get_dataframe()
        # data = pd.concat([
        #     data[(data.channel == 8) | (data.channel == 10)],
        #     data[(data.id == 61) | (data.id == 1960)]
        # ])
        if self.CONVERT_TO_REF or self.SUBTRACT_BB:
            for i, row in tqdm.tqdm(data.iterrows(), total=len(data), desc="Calculating deviations by surface"):
                area = FY3DImageArea.get(id=row.id)
                image = area.image
                area_avg = row.area_avg
                if self.SUBTRACT_BB:
                    area_avg -= area.get_black_body_value(row.channel)
                if self.CONVERT_TO_REF:
                    sensor_avg = area_avg + row.deviation
                    area_avg_Ref = some_utils.DN_to_Ref(area_avg, image, row.channel)
                    sensor_avg_Ref = some_utils.DN_to_Ref(sensor_avg, image, row.channel)
                    deviation_Ref = sensor_avg_Ref - area_avg_Ref
                    data.loc[i, "deviation"] = deviation_Ref
                    data.loc[i, "area_avg"] = area_avg_Ref
        self.result = data


class DeviationsByMirrorSide(BaseTask):
    task_name = "Отклонения в зависимости от яркости и зеркала"

    def calculate_data(self):
        self.result = Deviations.get_dataframe()


class RegressByYear(BaseTask):
    """Вычисляет линии регрессий по разным годам
    Поля result:
        Таблица coefficients:
            year:               Год
            channel:            Номер канала
            sensor:             Номер датчика
            k_mirror_side:      Сторона зеркала
            slope:              Коэффициент наклона
            intercept:          Коэффициент подъёма
            r^2:                Коэффициент детерминации
            pvalue:             p-значение
            slope_stderr:       Ст. ошибка коэффициента наклона
            intercept_stderr:   Ст. ошибка коэффициента подъёма
            avg_deviation:      Среднее значение отклонений
            std_deviation:      Ст. отклонение отклонений

        Таблица data_count:
            year:           Год
            total_count:    Общее кол-во областей
            mirror_1_count: Кол-во областей, снятых стороной зеркала 1
            mirror_2_count: Кол-во областей, снятых стороной зеркала 2
            sea_count:      Кол-во областей, содержащих море
            snow_count:     Кол-во областей, содержащих снег

        Таблица ranges:
            channel:    Номер канала
            x_min:      Минимальный x
            x_max:      Максимальный x
            y_min:      Минимальный y
            y_max:      Максимальный y
    """
    task_name = "Линии регрессии по годам"

    def calculate_data(self):
        years = [2020, 2021, 2022, 2023]
        coefficients = pd.DataFrame(columns=["year", "channel", "sensor", "k_mirror_side", "slope", "intercept",
                                             "r^2", "pvalue", "slope_stderr", "intercept_stderr",
                                             "avg_deviation", "std_deviation"])
        data_count = pd.DataFrame(columns=["year", "total_count", "mirror_1_count", "mirror_2_count",
                                           "sea_count", "snow_count"])
        ranges = pd.DataFrame(columns=["channel", "x_min", "x_max", "y_min", "y_max"])
        for channel in range(5, 20):
            sensor_data = Deviations.get_dataframe(channel=channel)
            x_min = sensor_data["area_avg"].min()
            x_max = sensor_data["area_avg"].max()
            y_min = sensor_data["deviation"].min()
            y_max = sensor_data["deviation"].max()
            ranges.loc[len(ranges)] = [channel, x_min, x_max, y_min, y_max]

        with tqdm.tqdm(total=15 * 10 * len(years), desc="Calculating coefficients for years") as pbar:
            for year in years:

                # Добавляем данные о количестве данных за год
                total_count = Deviations.get_count(year=year, channel=5, sensor=0)
                side_1_count = Deviations.get_count(year=year, channel=5, sensor=0, k_mirror_side=KMirrorSide.SIDE_1)
                side_2_count = Deviations.get_count(year=year, channel=5, sensor=0, k_mirror_side=KMirrorSide.SIDE_2)
                sea_count = Deviations.get_count(year=year, channel=5, sensor=0, surface_type=SurfaceType.SEA)
                snow_count = Deviations.get_count(year=year, channel=5, sensor=0, surface_type=SurfaceType.SNOW)
                data_count.loc[len(data_count)] = [year, total_count, side_1_count, side_2_count,
                                                   sea_count, snow_count]

                # Вычисляем отклонения
                for channel in range(5, 20):
                    for sensor_i in range(10):
                        side_1_data = Deviations.get_dataframe(year=year, channel=channel, sensor=sensor_i,
                                                               k_mirror_side=KMirrorSide.SIDE_1)
                        side_2_data = Deviations.get_dataframe(year=year, channel=channel, sensor=sensor_i,
                                                               k_mirror_side=KMirrorSide.SIDE_2)
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

                        coefficients.loc[len(coefficients)] = [year, channel, sensor_i, KMirrorSide.SIDE_1.value,
                                                               slope_1, intercept_1,
                                                               linreg_side_1.rvalue ** 2, linreg_side_1.pvalue,
                                                               linreg_side_1.stderr,
                                                               linreg_side_1.intercept_stderr,
                                                               y_side_1.mean(), y_side_1.std()]
                        coefficients.loc[len(coefficients)] = [year, channel, sensor_i, KMirrorSide.SIDE_2.value,
                                                               slope_2, intercept_2,
                                                               linreg_side_2.rvalue ** 2, linreg_side_2.pvalue,
                                                               linreg_side_2.stderr,
                                                               linreg_side_2.intercept_stderr,
                                                               y_side_1.mean(), y_side_1.std()]
                        pbar.update(1)
        self.result = {
            "coefficients": coefficients,
            "data_count": data_count,
            "ranges": ranges
        }


class NeighboringMirrorsDifference(BaseTask):
    """
    Находит области, которые находятся близко друг к другу и на разных зеркалах и находит их разницу
    Поля result:
        Таблица whole_area:
            channel:    Номер канала
            difference: Разница между областями
            avg_value:  Средняя яркость по двум областям

        Таблица each_sensor:
            channel:    Номер канала
            sensor:     Номер сенсора
            difference: Разница между областями
            avg_value:  Средняя яркость по двум областям
    """
    task_name = "Разница между соседними областями зеркал"

    def get_neighboring_areas(self, img: FY3DImage) -> list[tuple[FY3DImageArea, FY3DImageArea]]:
        """Возвращает список соседствующих областей на снимке img.
        При этом первый элемент принадлежит первому зеркалу, второй - второму зеркалу"""
        areas = list(img.selected_areas())
        neighbors = []
        max_x_diff = 40
        while areas:
            area_1 = areas.pop()
            for i, area_2 in enumerate(areas):
                if abs(area_1.y - area_2.y) == 10 and abs(area_1.x - area_2.x) <= max_x_diff:
                    if area_1.get_mirror_side() == KMirrorSide.SIDE_2:
                        area_1, area_2 = area_2, area_1
                    neighbors.append((area_1, area_2))
                    del areas[i]
                    break
        return neighbors

    def calculate_data(self) -> None:
        areas_count = FY3DImageArea.select() \
            .join(FY3DImage) \
            .where((FY3DImageArea.is_selected == True) & (FY3DImage.is_selected == True)) \
            .count()
        whole_area = pd.DataFrame(columns=[
            "channel",
            "difference",
            "avg_value",
        ], index=range(areas_count * 15))
        each_sensor = pd.DataFrame(columns=[
            "channel",
            "sensor",
            "difference",
            "avg_value",
        ], index=range(areas_count * 150))
        curr_i = 0
        for image in tqdm.tqdm(FY3DImage.selected_images(), desc="Calculating neighbors on images"):
            for area_1, area_2 in self.get_neighboring_areas(image):
                for channel in range(5, 20):
                    area_1_avg = area_1.get_channel_avg(channel)
                    area_2_avg = area_2.get_channel_avg(channel)
                    difference = area_1_avg - area_2_avg
                    avg_value = (area_1_avg + area_2_avg) / 2
                    whole_area.loc[curr_i] = [channel, difference, avg_value]
                    for sensor in range(10):
                        sensor_1_avg = list(Deviations.select()
                                            .where((Deviations.area == area_1)
                                                   & (Deviations.channel == channel)
                                                   & (Deviations.sensor == sensor)))[0].sensor_avg
                        sensor_2_avg = list(Deviations.select()
                                            .where((Deviations.area == area_2)
                                                   & (Deviations.channel == channel)
                                                   & (Deviations.sensor == sensor)))[0].sensor_avg
                        sensor_difference = sensor_1_avg - sensor_2_avg
                        sensor_avg_value = (sensor_1_avg + sensor_2_avg) / 2
                        each_sensor.loc[curr_i * 10 + sensor] = [channel, sensor, sensor_difference, sensor_avg_value]
                    curr_i += 1

        self.result = {
            "whole_area": whole_area.dropna(),
            "each_sensor": each_sensor.dropna()
        }


class FindSpectreBrightness(BaseTask):
    """Берёт несколько областей на воде и льду и для каждого канала находит среднюю яркость
    Поля result:
        Таблица sea:
            area_id:    Номер области
            channel:    Номер канала
            area_avg:   Средняя яркость области

        Таблица snow:
            area_id:    Номер области
            channel:    Номер канала
            area_avg:   Средняя яркость области
    """
    task_name = "Нахождение спектра"

    CONVERT_TO_REF = True
    SUBTRACT_BB = True

    def calculate_data(self) -> None:
        sea = pd.DataFrame(columns=["area_id", "channel", "area_avg"])
        snow = pd.DataFrame(columns=["area_id", "channel", "area_avg"])
        areas_count = 10
        areas = FY3DImageArea.selected_areas()
        sea_areas = list(areas.where(FY3DImageArea.surface_type == SurfaceType.SEA.value).dicts())
        snow_areas = list(areas.where(FY3DImageArea.surface_type == SurfaceType.SNOW.value).dicts())

        random.Random(2).shuffle(sea_areas)
        random.Random(2).shuffle(snow_areas)
        sea_areas = sea_areas[:areas_count]
        snow_areas = snow_areas[:areas_count]
        for area_info in sea_areas:
            area = FY3DImageArea.get(id=area_info["id"])
            for channel in range(5, 20):
                ch_area_avg = area.get_vis_channel(channel).mean()
                if self.SUBTRACT_BB:
                    ch_area_avg -= area.get_black_body_value(channel)
                if self.CONVERT_TO_REF:
                    ch_area_avg = some_utils.DN_to_Ref(ch_area_avg, area.image, channel)
                sea.loc[len(sea)] = [area.id, channel, ch_area_avg]
        for area_info in snow_areas:
            area = FY3DImageArea.get(id=area_info["id"])
            for channel in range(5, 20):
                ch_area_avg = area.get_vis_channel(channel).mean()
                if self.SUBTRACT_BB:
                    ch_area_avg -= area.get_black_body_value(channel)
                if self.CONVERT_TO_REF:
                    ch_area_avg = some_utils.DN_to_Ref(ch_area_avg, area.image, channel)
                snow.loc[len(snow)] = [area.id, channel, ch_area_avg]
        self.result = {
            "sea": sea,
            "snow": snow
        }


class DeviationsByY(BaseTask):
    task_name = "Отклонения в зависимости от координаты Y"

    def calculate_data(self) -> None:
        self.result = Deviations.get_dataframe()


DATABASE_TASKS = [
    SensorsCoefficientsTaskByMirror,
    SensorsCoefficientsTaskBySurface,
    SensorsCoefficientsTask,
    AreaAvgStdTask,
    DeviationsBySurface,
    DeviationsByMirrorSide,
    RegressByYear,
    NeighboringMirrorsDifference,
    FindSpectreBrightness,
    DeviationsByY,
]
DICT_DATABASE_TASKS = {task.task_name: task for task in DATABASE_TASKS}
