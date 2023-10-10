from database import FY3DImage
from tasks.BaseTasks import *
from abc import ABC
from utils.save_data_utils import *


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

    def calculate_data(self):
        columns = ["channel", "img_name", "c1", "c2", "c3"]
        df = pd.DataFrame(columns=columns)
        for ch in range(5, 20):
            ch_i = ch - 5
            for image in self.images:
                coeffs = image.VIS_Cal_Coeff[ch_i].tolist()
                row = [ch, image.get_unique_name(), *coeffs]
                df.loc[len(df)] = row
        self.result = df


MULTI_IMAGE_TASKS = [
    MultipleImagesCalibrationTask,
]
DICT_MULTI_IMAGE_TASKS = {task.task_name: task for task in MULTI_IMAGE_TASKS}
