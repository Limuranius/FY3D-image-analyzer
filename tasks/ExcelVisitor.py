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
        data = task.get_data()
        sheets = []
        channels = data["channel"].unique()
        channels.sort()
        for ch in channels:
            filt = data["channel"] == ch
            header = ["Дата снимка", "Коэф. 1", "Коэф. 2", "Коэф. 3"]
            sheet_data = (data[filt].drop(columns=["channel"])
                          .sort_values("img_date")
                          .values.tolist())
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

    def visit_NeighboringMirrorsDifference(self, task: DatabaseTasks.NeighboringMirrorsDifference):
        data = task.get_data()
        whole_area = data["whole_area"]
        each_sensor = data["each_sensor"]

        whole_area_sheet = [
            ["Канал"] + [f"Канал {ch}" for ch in range(5, 20)],
            ["Ср. разница"]
        ]
        for channel in range(5, 20):
            whole_area_sheet[1].append(
                whole_area[whole_area.channel == channel].difference.mean()
            )

        each_sensor_sheet = [
            [""] + [f"Канал {ch}" for ch in range(5, 20)],
        ]
        for sensor in range(10):
            row = [f"Датчик {sensor}"]
            for channel in range(5, 20):
                sensor_data = each_sensor[(each_sensor.channel == channel) & (each_sensor.sensor == sensor)]
                row.append(sensor_data.difference.mean())
            each_sensor_sheet.append(row)

        path = get_excel_path_and_create(task, "Разница между зеркалами")
        sheets = [
            ("Среднее по всей области", whole_area_sheet),
            ("Среднее по каждому датчику", each_sensor_sheet)
        ]
        save_data_utils.save_excel(path, sheets)

    def visit_FindSpectreBrightness(self, task: DatabaseTasks.FindSpectreBrightness):
        data = task.get_data()
        sea = data["sea"]
        snow = data["snow"]

        sea_sheet = [
            [""] + [f"Канал {ch}" for ch in range(5, 20)]
        ]
        for area_id in sea.area_id.unique():
            area_data = sea[sea.area_id == area_id].sort_values(by="channel")
            sea_sheet.append([
                area_id,
                *area_data.area_avg
            ])

        snow_sheet = [
            [""] + [f"Канал {ch}" for ch in range(5, 20)]
        ]
        for area_id in snow.area_id.unique():
            area_data = snow[snow.area_id == area_id].sort_values(by="channel")
            snow_sheet.append([
                area_id,
                *area_data.area_avg
            ])

        sheets = [
            ("Вода", sea_sheet),
            ("Лёд", snow_sheet)
        ]
        path = get_excel_path_and_create(task, "Спектры")
        save_data_utils.save_excel(path, sheets)
