import numpy as np
import pandas as pd

from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
from .BaseTasks import *
from utils.area_utils import filter_areas_by_mirror_side, ch_area_rows_deviations
from vars import KMIRROR_SIDE, SurfaceType, KMirrorSide
from abc import ABC
from .ImageTasks import SensorSystemErrorTask2
from utils.Table import Table
from utils.save_data_utils import *
# from utils.utils import *
from scipy.stats import linregress


class BaseMultipleImagesTask(BaseTask, ABC):
    images: list[FY3DImage]

    def __init__(self, images: list[FY3DImage]):
        super().__init__()
        self.images = images
        self.obj_name = self.task_name

    def get_areas(self, image: FY3DImage) -> list[FY3DImageArea]:
        return image.areas

    def count_total_areas(self) -> int:
        count = 0
        for image in self.images:
            count += len(image.areas)
        return count


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


class AllAreasDeviations(BaseMultipleImagesTask):
    """Вспомогательный метод. Высчитывает отклонения всех датчиков и другую дополнительную информацию
    Поля таблицы data:
        Канал
        Название области
        Ср. яркость области
        Номер датчика
        Отклонение датчика в этой области
        Тип поверхности области
        Год снимка
    """
    task_name = "Отклонение датчиков по всем областям"

    def calculate_data(self):
        columns = ["channel", "name", "area_avg", "sensor_i", "sensor_deviation", "surface_type", "mirror_side", "year"]
        df = pd.DataFrame(index=range(self.count_total_areas() * 150), columns=columns)
        curr_i = 0
        for channel in range(5, 20):
            for image in self.images:
                for area in self.get_areas(image):
                    ch_area = area.get_vis_channel(channel)
                    deviations = ch_area_rows_deviations(ch_area)
                    area_avg = ch_area.mean()
                    for sensor_i in range(0, 10):
                        sensor_deviation = deviations[sensor_i]
                        row = [channel, area.name, area_avg, sensor_i, sensor_deviation, area.surface_type,
                               area.get_mirror_side(), image.get_year()]
                        df.loc[curr_i] = row
                        curr_i += 1
        return df


class DeviationsLinearRegression(BaseMultipleImagesTask):
    """Находит отклонение каждого датчика в каждой области каждого снимка и яркость этой области"""
    task_name = "Линейная регрессия зависимости отклонения от яркости"

    def get_areas(self, image: FY3DImage) -> list[FY3DImageArea]:
        return filter_areas_by_mirror_side(image.areas, KMIRROR_SIDE)

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()

    def save_excel(self, data: pd.DataFrame):
        for channel in range(5, 20):
            path = self.get_excel_path(f"Канал {channel}")
            sheets = []
            for sensor_i in range(10):
                sheet_name = f"Датчик {sensor_i}"
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                # sheet_data = data.loc[filt, ["area_avg", "sensor_deviation"]]
                # sheet_data.rename(columns={"area_avg": "Яркость области", "sensor_deviation": "Отклонение датчика"},
                #                   inplace=True)
                sheet_data = data.loc[filt, ["name", "area_avg", "sensor_deviation"]]
                sheet_data.rename(columns={"area_avg": "Яркость области", "sensor_deviation": "Отклонение датчика"},
                                  inplace=True)
                sheets.append((sheet_name, sheet_data))
            save_excel_dataframe(path, sheets, header=True)

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
                k, b, r_sq = linregress(x, y)
                sheet_data.loc[f"Датчик {sensor_i}"] = [k, b, r_sq]
            sheets.append((sheet_name, sheet_data))
        path = self.get_excel_path("Коэффициенты прямых")
        save_excel_dataframe(path, sheets, index=True, header=True)

    def save_graphs(self, data):
        for channel in range(5, 20):
            for sensor_i in range(10):
                path = self.get_graph_img_path(f"Канал {channel}/Датчик {sensor_i}")
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                graph_data = data.loc[filt]
                x = graph_data["area_avg"].to_numpy()
                y = graph_data["sensor_deviation"].to_numpy()

                regress = linregress(x.astype(float), y.astype(float))
                slope = regress.slope
                intercept = regress.intercept
                rvalue = regress.rvalue
                pvalue = regress.pvalue
                stderr = regress.stderr
                intercept_stderr = regress.intercept_stderr

                line_x0 = x.min()
                line_x1 = x.max()
                line_y0 = line_x0 * slope + intercept
                line_y1 = line_x1 * slope + intercept

                text = "slope={:.4f} intercept={:.4f}\nR^2={:.4f} pvalue={:.4f}\nstderr={:.4f} intercept_stderr={:.4f}" \
                    .format(slope, intercept, rvalue ** 2, pvalue, stderr, intercept_stderr)

                create_and_save_figure(path, y_rows=[y, [line_y0, line_y1]], x_rows=[x, [line_x0, line_x1]],
                                       title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости",
                                       xlabel="Яркость", ylabel="Отклонение датчика", fmt_list=[".", "--"],
                                       text=text)


class DeviationsBySurface(BaseMultipleImagesTask):
    task_name = "Отклонения в зависимости от яркости и поверхности"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()

    def save_graphs(self, data):
        for channel in range(5, 20):
            for sensor_i in range(10):
                path = self.get_graph_img_path(f"Канал {channel}/Датчик {sensor_i}")
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                ch_sens_data = data.loc[filt]
                filt_sea = ch_sens_data["surface_type"] == SurfaceType.SEA
                filt_snow = ch_sens_data["surface_type"] == SurfaceType.SNOW
                sea_data = ch_sens_data.loc[filt_sea]
                snow_data = ch_sens_data.loc[filt_snow]

                x_sea = sea_data["area_avg"].to_numpy()
                y_sea = sea_data["sensor_deviation"].to_numpy()
                x_snow = snow_data["area_avg"].to_numpy()
                y_snow = snow_data["sensor_deviation"].to_numpy()

                create_and_save_figure(path, y_rows=[y_sea, y_snow], x_rows=[x_sea, x_snow],
                                       title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости",
                                       xlabel="Яркость", ylabel="Отклонение датчика", fmt_list=[".", "."],
                                       legend_title="Тип поверхности", legend=["Море", "Снег"])


class DeviationsByMirrorSide(BaseMultipleImagesTask):
    task_name = "Отклонения в зависимости от яркости и зеркала"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()

    def save_graphs(self, data):
        for channel in range(5, 20):
            for sensor_i in range(10):
                path = self.get_graph_img_path(f"Канал {channel}/Датчик {sensor_i}")

                # Фильтруем данные по каналу и датчику
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                ch_sens_data = data.loc[filt]

                # Фильтруем данные по стороне зеркала
                filt_side_1 = ch_sens_data["mirror_side"] == KMirrorSide.SIDE_1
                filt_side_2 = ch_sens_data["mirror_side"] == KMirrorSide.SIDE_2
                side_1_data = ch_sens_data.loc[filt_side_1]
                side_2_data = ch_sens_data.loc[filt_side_2]
                x_side_1 = side_1_data["area_avg"].to_numpy()
                y_side_1 = side_1_data["sensor_deviation"].to_numpy()
                x_side_2 = side_2_data["area_avg"].to_numpy()
                y_side_2 = side_2_data["sensor_deviation"].to_numpy()

                # Находим линии регрессии для первого и второго зеркала
                slope_side_1, intercept_side_1, *_ = linregress(x_side_1.astype(float), y_side_1.astype(float))
                slope_side_2, intercept_side_2, *_ = linregress(x_side_2.astype(float), y_side_2.astype(float))
                line_x0_side_1 = x_side_1.min()
                line_x1_side_1 = x_side_1.max()
                line_y0_side_1 = line_x0_side_1 * slope_side_1 + intercept_side_1
                line_y1_side_1 = line_x1_side_1 * slope_side_1 + intercept_side_1
                line_x0_side_2 = x_side_2.min()
                line_x1_side_2 = x_side_2.max()
                line_y0_side_2 = line_x0_side_2 * slope_side_2 + intercept_side_2
                line_y1_side_2 = line_x1_side_2 * slope_side_2 + intercept_side_2

                create_and_save_figure(path,
                                       y_rows=[y_side_1, y_side_2, [line_y0_side_1, line_y1_side_1],
                                               [line_y0_side_2, line_y1_side_2]],
                                       x_rows=[x_side_1, x_side_2, [line_x0_side_1, line_x1_side_1],
                                               [line_x0_side_2, line_x1_side_2]],
                                       title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости",
                                       xlabel="Яркость", ylabel="Отклонение датчика", fmt_list=[".", ".", "--", "--"],
                                       legend_title="Сторона зеркала", legend=["Первая", "Вторая", "Первая", "Вторая"])


class DeviationsMeanPerImage(BaseMultipleImagesTask):
    task_name = "Отклонения по средним по снимку"

    def calculate_data(self):
        columns = ["channel", "img_name", "sensor_i", "deviation", "ch_avg"]
        df = pd.DataFrame(index=range(len(self.images) * 150), columns=columns)
        curr_i = 0
        for channel in range(5, 20):
            for image in self.images:
                sum_brightness = 0
                pixel_count = 0
                for area in self.get_areas(image):
                    ch_area = area.get_vis_channel(channel)
                    sum_brightness += ch_area.sum()
                    pixel_count += ch_area.size
                ch_avg = sum_brightness / pixel_count
                for sensor_i in range(10):
                    sum_sens_brightness = 0
                    sens_pixel_count = 0
                    for area in self.get_areas(image):
                        ch_area = area.get_vis_channel(channel)
                        sum_sens_brightness += ch_area[sensor_i].sum()
                        sens_pixel_count += ch_area[sensor_i].size
                    sensor_avg = sum_sens_brightness / sens_pixel_count
                    sensor_deviation = sensor_avg - ch_avg
                    row = [channel, image.name, sensor_i, sensor_deviation, ch_avg]
                    df.loc[curr_i] = row
                    curr_i += 1
        return df

    def save_graphs(self, data):
        for channel in range(5, 20):
            for sensor_i in range(10):
                path = self.get_graph_img_path(f"Канал {channel}/Датчик {sensor_i}")

                # Фильтруем данные по каналу и датчику
                filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                ch_sens_data = data.loc[filt]

                x = ch_sens_data["ch_avg"].to_numpy()
                y = ch_sens_data["deviation"].to_numpy()

                # slope, intercept, *_ = linregress(x.astype(float), y.astype(float))

                create_and_save_figure(path,
                                       y_rows=[y],
                                       x_rows=[x],
                                       title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости",
                                       xlabel="Яркость", ylabel="Отклонение датчика", fmt_list=["."])


class RegressByYear(BaseMultipleImagesTask):
    task_name = "Линии регрессии по годам"

    def calculate_data(self):
        t = AllAreasDeviations(self.images)
        return t.calculate_data()

    def save_graphs(self, data):
        years = data["year"].unique().tolist()
        years.sort()

        for channel in range(5, 20):
            for sensor_i in range(10):
                path = self.get_graph_img_path(f"Канал {channel}/Датчик {sensor_i}")
                years_x = []  # Координаты x точек начала и конца регрессионных линий
                years_y = []  # Координаты y точек начала и конца регрессионных линий
                for year in years:
                    # Фильтруем данные по каналу, датчику и году
                    filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i) & (data["year"] == year)
                    ch_sens_data = data.loc[filt]

                    x = ch_sens_data["area_avg"].to_numpy()
                    y = ch_sens_data["sensor_deviation"].to_numpy()

                    # Находим линии регрессии
                    slope, intercept, *_ = linregress(x.astype(float), y.astype(float))
                    line_x0 = x.min()
                    line_x1 = x.max()
                    line_y0 = line_x0 * slope + intercept
                    line_y1 = line_x1 * slope + intercept

                    years_x.append([line_x0, line_x1])
                    years_y.append([line_y0, line_y1])

                create_and_save_figure(path,
                                       y_rows=years_y,
                                       x_rows=years_x,
                                       title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости по годам",
                                       xlabel="Яркость", ylabel="Отклонение датчика",
                                       fmt_list=["-"] * len(years),
                                       legend_title="Год",
                                       legend=years)


MULTI_IMAGE_TASKS = [
    DeviationsAcrossImages,
    DeviationsLinearRegression,
    DeviationsBySurface,
    DeviationsByMirrorSide,
    DeviationsMeanPerImage,
    RegressByYear
]
DICT_MULTI_IMAGE_TASKS = {task.task_name: task for task in MULTI_IMAGE_TASKS}
