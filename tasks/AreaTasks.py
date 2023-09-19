from .BaseTasks import *
from FY3DImageArea import FY3DImageArea
import numpy as np
from utils.save_data_utils import save_excel, create_and_save_figure
from math import sqrt


class BaseAreaTask(BaseTask, ABC):
    area: FY3DImageArea

    def __init__(self, area: FY3DImageArea):
        self.area = area
        super().__init__()


class SensorMeanRowDeviation(BaseAreaTask):
    """
    Для каждого пикселя находится его отклонение от среднего по строке
    Поля result:
        channel:    Номер канала
        sens_i:     Номер датчика
        deviations:  Массив отклонений пикселей
    """
    task_name = "Способ 1 (Отклонение от среднего по строке)"

    def calculate_data(self) -> pd.DataFrame:
        columns = ["channel", "sens_i", "deviations"]
        df = pd.DataFrame(columns=columns)
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Вычитаем из каждой строки её среднее значение
            for sens_i in range(height):
                row_avg = ch_area[sens_i].mean()
                deviations = ch_area[sens_i] - row_avg
                row = [channel, sens_i, deviations]
                df.loc[len(df)] = row
        return df


class SensorMeanColumnDeviation(BaseAreaTask):
    """
    Для каждого пикселя находится его отклонение от среднего по столбцу
    Поля result:
        channel:    Номер канала
        sens_i:     Номер датчика
        deviations:  Массив отклонений пикселей
    """
    task_name = "Способ 2 (Отклонение от среднего по столбцу)"

    def calculate_data(self) -> pd.DataFrame:
        columns = ["channel", "sens_i", "deviations"]
        df = pd.DataFrame(columns=columns)
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Вычитаем из каждого столбца его среднее значение
            for col in range(width):
                col_avg = ch_area[:, col].mean()
                ch_area[:, col] -= col_avg
            for sens_i in range(height):
                deviations = ch_area[sens_i]
                row = [channel, sens_i, deviations]
                df.loc[len(df)] = row
        return df


class AreaMean(BaseAreaTask):
    """
    У каждого столбца пикселей находим среднее
    Поля result:
        channel:    Номер канала
        avg_cols:     Массив значений
    """
    task_name = "Способ 3 (Средние значения столбцов)"

    def calculate_data(self):
        columns = ["channel", "avg_cols"]
        df = pd.DataFrame(columns=columns)
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)

            # Находим среднее значение каждого столбца
            avg_cols = ch_area.mean(axis=0)
            df.loc[len(df)] = [channel, avg_cols]
        return df


AREA_TASKS = [
    SensorMeanRowDeviation,
    SensorMeanColumnDeviation,
    AreaMean,
]
DICT_AREA_TASKS = {task.task_name: task for task in AREA_TASKS}
