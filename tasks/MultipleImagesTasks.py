import numpy as np

from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
from .BaseTasks import *
from utils.area_utils import filter_areas_by_mirror_side
from vars import KMIRROR_SIDE
from abc import ABC
from .ImageTasks import SensorSystemErrorTask2
from utils.Table import Table
from utils.save_data_utils import save_excel


class BaseMultipleImagesTask(BaseTask, ABC):
    images: list[FY3DImage]

    def __init__(self, images: list[FY3DImage]):
        super().__init__()
        self.images = images
        self.obj_name = self.task_name

    def get_areas(self, image: FY3DImage) -> list[FY3DImageArea]:
        return image.areas


class DeviationsAcrossImages(BaseMultipleImagesTask):
    """
    Для каждого снимка находит средние отклонения датчиков
    Формат data:
    (
        Канал,
        [][] Отклонения j-ых датчиков на i-ых снимках
    )
    """
    task_name = "Сравнение датчиков по снимкам"

    def get_areas(self, image: FY3DImage) -> list[FY3DImageArea]:
        return filter_areas_by_mirror_side(image.areas, KMIRROR_SIDE)

    def calculate_data(self):
        data = []
        for ch in range(5, 20):
            h = len(self.images)
            w = 10
            deviations = np.ndarray((h, w), dtype=np.float64)
            for i, image in enumerate(self.images):
                image_deviations_task = SensorSystemErrorTask2(image)
                image_deviations_data = image_deviations_task.calculate_data()
                _, _, sensors_avg_deviations, _ = image_deviations_data[ch - 5]
                deviations[i] = sensors_avg_deviations
            data.append((ch, deviations.tolist()))
        return data

    def save_excel(self, data):
        sheets = []
        for ch, deviations in data:
            hh = ["Снимок"] + [f"Датчик {i}" for i in range(0, 10)]
            vh = [image.get_name() for image in self.images]
            t = Table(horiz_head=hh, vert_head=vh)
            for img_deviations in deviations:
                t.append_row(img_deviations)
            sheets.append((
                f"Канал {ch}",
                [[f"Средняя разница между датчиками канала {ch} и средним области по всем областям снимка"]] +
                t.get_content()
            ))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)


# class MultipleImagesCalibrationTask:
#     images: list[FY3DImage]
#     task_name = "Калибровочные коэффициенты"
#
#     def __init__(self, images: list[FY3DImage]):
#         self.images = images
#         self.root_dir = os.path.join(vars.RESULTS_DIR, self.task_name)
#         # Создаём обработчика эксель файла
#         path = os.path.join(self.root_dir, "Калибровочные коэффициенты.xlsx")
#         utils.create_dirs(path)
#         self.excel_writer = pd.ExcelWriter(path)
#
#     def analyze(self):
#         for ch in range(5, 20):
#             sheet_data = [["Снимок", "Коэф. 1", "Коэф. 2", "Коэф. 3"]]
#             ch_i = ch - 5
#             for image in self.images:
#                 coeff = image.VIS_Cal_Coeff[ch_i].tolist()
#                 sheet_data.append([image.get_name()] + coeff)
#             pd.DataFrame(sheet_data).to_excel(self.excel_writer, f"Канал {ch}", header=False, index=False)
#         self.excel_writer.close()


MULTI_IMAGE_TASKS = [
    DeviationsAcrossImages
]
DICT_MULTI_IMAGE_TASKS = {task.task_name: task for task in MULTI_IMAGE_TASKS}