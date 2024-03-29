from .BaseVisitor import *
from utils import save_data_utils
import os
import vars
from scipy.stats import linregress


def get_excel_path_and_create(task, file_name: str, inner_dir: str = ""):
    """Для таски task находит путь excel-файла, создаёт его и возвращает
    inner_dir: Путь внутри папки таски. Например, если надо выделить папку для каждого снимка
    """
    excel_dir_path = os.path.join(vars.RESULTS_DIR, task.task_name, "Excel")
    path = os.path.join(excel_dir_path, inner_dir)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, file_name)
    if not file_path.endswith(".xlsx"):
        file_path += ".xlsx"
    return file_path


class ExcelVisitor(BaseVisitor):
    def visit_ImageBBTask(self, task: ImageTasks.BBTask):
        data = task.result
        sheet_data = [["Канал", "Данные Black Body"]]
        for ch_i in range(25):
            sheet_data.append([ch_i + 1, *data.loc[ch_i]["dataBB"]])
        sheets = [
            ("Black Body", sheet_data)
        ]
        path = get_excel_path_and_create(task, task.image.get_unique_name())
        save_data_utils.save_excel(path, sheets)

    def visit_ImageSVTask(self, task: ImageTasks.SVTask):
        data = task.result
        sheets = [
            ("Space View", data)
        ]
        path = get_excel_path_and_create(task, task.image.get_unique_name())
        save_data_utils.save_excel_dataframe(path, sheets, header=True)

    def visit_MultipleImagesCalibrationTask(self, task: MultipleImagesTasks.MultipleImagesCalibrationTask):
        data = task.result
        sheets = []
        channels = data["channel"].unique()
        channels.sort()
        for ch in channels:
            filt = data["channel"] == ch
            header = ["Снимок", "Коэф. 1", "Коэф. 2", "Коэф. 3"]
            sheet_data = data.loc[filt].tolist()
            sheets.append((
                f"Канал {ch}",
                [header, *sheet_data]
            ))
        path = get_excel_path_and_create(task, task.task_name)
        save_data_utils.save_excel(path, sheets)

    def visit_SensorsCoefficientsTask(self, task: DatabaseTasks.SensorsCoefficientsTask):
        data = task.get_data()
        path = get_excel_path_and_create(task, task.task_name)
        sheets = [
            ("Коэффициенты", data)
        ]
        save_data_utils.save_excel_dataframe(path, sheets, header=True)

    def visit_RegressByYear(self, task: DatabaseTasks.RegressByYear):
        data = task.get_data()
        coefficients = data["coefficients"]
        data_count = data["data_count"]
        path = get_excel_path_and_create(task, task.task_name)
        sheets = [
            ("Коэффициенты", coefficients),
            ("Количество данных", data_count),
        ]
        save_data_utils.save_excel_dataframe(path, sheets, header=True)
