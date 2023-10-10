import tasks.BaseTasks as BaseTasks
from abc import ABC
from database.FY3DImage import FY3DImage
from database.FY3DImageArea import FY3DImageArea
import pandas as pd


class BaseImageTask(BaseTasks.BaseTask, ABC):
    image: FY3DImage

    def __init__(self, image: FY3DImage):
        self.image = image
        self.obj_name = self.image.name
        super().__init__()

    def get_areas(self) -> list[FY3DImageArea]:
        return self.image.areas


class BBTask(BaseImageTask):
    """Просмотр яркости чёрного тела для разных каналов
    Поля result:
        channel:    Номер канала
        dataBB:     Массив значений чёрного тела для 10 строк снимка
    """
    task_name = "Black Body"

    def calculate_data(self) -> pd.DataFrame:
        bb = self.image.BB_DN_average
        columns = ["channel", "dataBB"]
        df = pd.DataFrame(index=range(25), columns=columns)
        for ch_i in range(25):
            ch_num = ch_i + 1
            df.loc[ch_i] = [ch_num, bb[ch_i]]
        return df


class SVTask(BaseImageTask):
    """Просмотр яркости космоса для разных каналов
    Поля result:
        channel:    Номер канала
        dataBB:     Массив значений космоса для 10 строк снимка
    """
    task_name = "Space View"

    def calculate_data(self) -> pd.DataFrame:
        sv = self.image.SV_DN_average
        columns = ["channel", "dataSV"]
        df = pd.DataFrame(index=range(19), columns=columns)
        for ch_i in range(19):
            ch_num = ch_i + 1
            df.loc[ch_i] = [ch_num, sv[ch_i]]
        return df


IMAGE_TASKS = [
    BBTask,
    SVTask,
]
DICT_IMAGE_TASKS = {task.task_name: task for task in IMAGE_TASKS}
