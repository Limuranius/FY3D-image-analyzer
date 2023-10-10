import pandas as pd

from tasks.BaseTasks import *
from utils.save_data_utils import *
import tqdm
from database import Deviations, AreaStats
from scipy.stats import linregress
from vars import KMirrorSide, SurfaceType
import vars
import os


class SensorsCoefficientsTask(BaseTask):
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
    task_name = "Вычислить коэффициенты"

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

    def calculate_data(self):
        self.result = Deviations.get_dataframe()


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


DATABASE_TASKS = [
    SensorsCoefficientsTask,
    AreaAvgStdTask,
    DeviationsBySurface,
    DeviationsByMirrorSide,
    RegressByYear
]
DICT_DATABASE_TASKS = {task.task_name: task for task in DATABASE_TASKS}
