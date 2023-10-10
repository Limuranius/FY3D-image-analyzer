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
        sheets = [
            ("Black Body", data)
        ]
        path = get_excel_path_and_create(task, task.image.get_unique_name())
        save_data_utils.save_excel_dataframe(path, sheets, header=True)

    def visit_ImageSVTask(self, task: ImageTasks.SVTask):
        data = task.result
        sheets = [
            ("Space View", data)
        ]
        path = get_excel_path_and_create(task, task.image.get_unique_name())
        save_data_utils.save_excel_dataframe(path, sheets, header=True)

    def visit_DeviationsLinearRegression(self, task: MultipleImagesTasks.DeviationsLinearRegression):
        data = task.result
        for channel in range(5, 20):
            path = get_excel_path_and_create(task, f"Канал {channel}")
            sheets = []
            for sensor_i in range(10):
                sheet_name = f"Датчик {sensor_i}"
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                sheet_data = data.loc[filt, ["name", "area_avg", "sensor_deviation"]]
                sheet_data.rename(columns={"area_avg": "Яркость области", "sensor_deviation": "Отклонение датчика"},
                                  inplace=True)
                sheets.append((sheet_name, sheet_data))
            save_data_utils.save_excel_dataframe(path, sheets, header=True)

        # Создаём один общий excel с коэффициентами прямых
        sheets = []
        for channel in range(5, 20):
            sheet_name = f"Канал {channel}"
            sheet_data = pd.DataFrame(index=[f"Датчик {ch}" for ch in range(10)], columns=["a", "b", "R^2"])
            for sensor_i in range(10):
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                sensor_data = data.loc[filt]
                x = sensor_data["area_avg"].to_numpy()
                y = sensor_data["sensor_deviation"].to_numpy()
                k, b, rval, *_ = linregress(x, y)
                r_sq = rval ** 2
                sheet_data.loc[f"Датчик {sensor_i}"] = [k, b, r_sq]
            sheets.append((sheet_name, sheet_data))
        path = get_excel_path_and_create(task, "Коэффициенты прямых")
        save_data_utils.save_excel_dataframe(path, sheets, index=True, header=True)

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
