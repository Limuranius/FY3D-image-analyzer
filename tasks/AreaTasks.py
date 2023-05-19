from .BaseTasks import *
from FY3DImageArea import FY3DImageArea
import logging
import numpy as np
from utils.save_data_utils import save_excel, create_and_save_figure
from math import sqrt
from utils.Table import Table


class BaseAreaTask(BaseTask, ABC):
    area: FY3DImageArea

    def __init__(self, area: FY3DImageArea):
        self.area = area
        self.obj_name = self.area.name
        super().__init__()


class Task1(BaseAreaTask):
    """
    Метод 1.
    Для каждой строки:
        Находим среднее значение - одно число на строку
        Для каждого пикселя находится отклонение от этого среднего
    """
    task_name = "Способ 1 (Отклонение от среднего по строке)"

    def calculate_data(self):
        data = []
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Вычитаем из каждой строки её среднее значение
            for row in range(height):
                row_avg = ch_area[row].mean()
                ch_area[row] -= row_avg

            data.append((channel, ch_area))
        return data

    def save_excel(self, data: list[tuple[int, np.ndarray]]):
        sheets = []
        for channel, ch_area in data:
            sheets.append((f"Канал {channel}", ch_area))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)

    def save_graphs(self, data: list[tuple[int, np.ndarray]]):
        for channel, res_area in data:
            height, width = res_area.shape
            x_rows = []
            y_rows = []
            for i in range(height):
                x = list(range(width))
                y = res_area[i]
                x_rows.append(x)
                y_rows.append(y)

            path = self.get_graph_img_path(f"Канал {channel}")
            create_and_save_figure(path, y_rows, x_rows=x_rows,
                                   title=f"График отклонения от среднего по строке для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Отклонение от среднего по строке",
                                   legend=list(range(height)), legend_title="Строка")


class Task2(BaseAreaTask):
    """
    Метод 2.
    Для каждого столбца:
        Находим среднее столбца
        Для каждого пикселя находится отклонение от этого среднего
    """
    task_name = "Способ 2 (Отклонение от среднего по столбцу)"

    def calculate_data(self):
        data = []
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Вычитаем из каждого столбца его среднее значение
            for col in range(width):
                col_avg = ch_area[:, col].mean()
                ch_area[:, col] -= col_avg
            data.append((channel, ch_area))
        return data

    def save_excel(self, data: list[tuple[int, np.ndarray]]):
        sheets = []
        for channel, res_area in data:
            sheets.append((f"Канал {channel}", res_area))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)

    def save_graphs(self, data: list[tuple[int, np.ndarray]]):
        for channel, res_area in data:
            height, width = res_area.shape
            x_rows = []
            y_rows = []
            for i in range(height):
                x = list(range(width))
                y = res_area[i]
                x_rows.append(x)
                y_rows.append(y)

            path = self.get_graph_img_path(f"Канал {channel}")
            create_and_save_figure(path, y_rows, x_rows=x_rows,
                                   title=f"График отклонения от среднего каждого столбца для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Отклонение от среднего по столбцу",
                                   legend=list(range(height)), legend_title="Строка")


class Task3(BaseAreaTask):
    """
    Метод 3.
        У каждого столбца находим среднее и отображаем его на графике
    """
    task_name = "Способ 3 (Средние значения столбцов)"

    def calculate_data(self):
        data = []
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Находим среднее значение каждого столбца
            avg_cols = []
            for col in range(width):
                avg_cols.append(ch_area[:, col].mean())
            data.append((channel, avg_cols))
        return data

    def save_excel(self, data: list[tuple[int, list]]):
        sheets = []
        for channel, avg_cols in data:
            sheets.append((f"Канал {channel}", avg_cols))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)

    def save_graphs(self, data: list[tuple[int, list]]):
        for channel, avg_cols in data:
            path = self.get_graph_img_path(f"Канал {channel}")
            create_and_save_figure(path, [avg_cols],
                                   title=f"График средних значений каждого столбца для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Среднее значение")


class Task4(BaseAreaTask):
    """
    Метод 4.
        У каждого столбца находим стандартное отклонение и отображаем его на графике
    """
    task_name = "Способ 4 (Стандартное отклонение столбцов)"

    def calculate_data(self):
        data = []
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Находим стандартное отклонение каждого столбца
            stds = []
            for col in range(width):
                stds.append(ch_area[:, col].std())
            data.append((channel, stds))
        return data

    def save_excel(self, data: list[tuple[int, list]]):
        sheets = []
        for channel, stds in data:
            sheets.append((f"Канал {channel}", stds))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)

    def save_graphs(self, data: list[tuple[int, list]]):
        for channel, stds in data:
            path = self.get_graph_img_path(f"Канал {channel}")
            create_and_save_figure(path, [stds],
                                   title=f"График стандартного отклонения каждого столбца для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Стандартное отклонение")


class Task5(BaseAreaTask):
    """
    Метод 5.
        Находим среднее по всей области
        У каждого пикселя находим отклонение от этого среднего
    """
    task_name = "Способ 5 (Отклонение от общего среднего)"

    def calculate_data(self):
        data = []
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)

            # Находим отклонение каждого пикселя от общего среднего
            avg = ch_area.mean()
            ch_area -= avg
            data.append((channel, ch_area))
        return data

    def save_excel(self, data: list[tuple[int, np.ndarray]]):
        sheets = []
        for channel, res_area in data:
            sheets.append((f"Канал {channel}", res_area))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)

    def save_graphs(self, data: list[tuple[int, np.ndarray]]):
        for channel, res_area in data:
            height, width = res_area.shape
            x_rows = []
            y_rows = []
            for i in range(height):
                x = list(range(width))
                y = res_area[i]
                x_rows.append(x)
                y_rows.append(y)

            path = self.get_graph_img_path(f"Канал {channel}")
            create_and_save_figure(path, y_rows, x_rows=x_rows,
                                   title=f"График отклонения от общего среднего для каждой строки\nдля канала {channel}",
                                   xlabel="Номер столбца", ylabel="Отклонение от общего среднего",
                                   legend=list(range(height)), legend_title="Строка")


class TaskNoise1_1(BaseAreaTask):
    """
    Нахождение среднего, стандартного отклонения и случайной ошибки каждой строки
    Формат data:
    (
        Канал,
        Стандартное отклонение области,
        Среднее значение области,
        [Стандартное отклонение строки],
        [Среднее значение строки],
        [Случайная ошибка строки]
    )
    """
    task_name = "Шумы 1.1 (случайная ошибка строки)"

    def calculate_data(self):
        data = []
        height = self.area.height
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            area_std = ch_area.std()
            area_avg = ch_area.std()
            rows_std = []
            rows_avg = []
            rows_error = []
            for i in range(height):
                row = ch_area[i]
                row_std = row.std()
                row_avg = row.mean()
                row_error = row_std / sqrt(len(row))
                rows_std.append(row_std)
                rows_avg.append(row_avg)
                rows_error.append(row_error)
            data.append((
                channel,
                area_std,
                area_avg,
                rows_std,
                rows_avg,
                rows_error
            ))
        return data

    def save_excel(self, data):
        std_table = Table(horiz_head=[["Строка"] + [f"Канал {ch}" for ch in range(5, 20)]],
                          vert_head=["Std области: "] + list(range(10)))
        error_table = Table(horiz_head=[["Строка"] + [f"{ch} канал" for ch in range(5, 20)]], vert_head=list(range(10)))
        avg_table = Table(horiz_head=[["Строка"] + [f"{ch} канал" for ch in range(5, 20)]], vert_head=list(range(10)))

        for ch_data in data:
            channel, area_std, area_avg, rows_std, rows_avg, rows_error = ch_data
            std_table.append_col([area_std] + rows_std)
            avg_table.append_col(rows_avg)
            error_table.append_col(rows_error)

        sheets = [
            ("Стандартное отклонение", std_table.get_content()),
            ("Случайная ошибка", error_table.get_content()),
            ("Среднее значение", avg_table.get_content())
        ]

        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)


# TODO: Переделать под новый код
# class TaskNoise1_2(BaseAreaTask):
#     """
#     Нахождение стандартного отклонения и случайной ошибки для всей области
#     Нахождение общего среднего области и отклонения среднего каждой строки от этого общего среднего
#     """
#     task_name = "Шумы 1.2 (отклонение от общего среднего)"
#
#     def analyze(self, draw_graphs: bool = False):
#         self.save_excel()
#         self.excel_writer.close()
#         logging.info(f"Шумы 1.2 завершён")
#
#     def save_excel(self):
#         height = self.area.height
#         width = self.area.width
#
#         # Таблицы с заполненными заголовками
#         ch_std_table = [["Канал", "Стандартное отклонение", "Случайная ошибка"]]
#         avg_divergence_table = [["Строка"] + [f"{ch} канал" for ch in range(5, 20)],
#                                 ["Среднее области", ]]
#         for i in range(height):
#             avg_divergence_table.append([i, ])
#
#         for channel in range(5, 20):
#             ch_area = self.area.get_vis_channel(channel)
#             area_std = ch_area.std()
#             area_avg = ch_area.mean()
#             area_error = area_std / sqrt(height * width)
#
#             ch_std_table.append([channel, area_std, area_error])
#             avg_divergence_table[1].append(area_avg)
#
#             for i in range(height):
#                 row = ch_area[i]
#                 row_avg = row.mean()
#                 avg_divergence_table[i + 2].append(row_avg - area_avg)
#
#         df_ch_std = pd.DataFrame(ch_std_table)
#         df_avg_divergence = pd.DataFrame(avg_divergence_table)
#         df_ch_std.to_excel(self.excel_writer, "Std и случ. ошибка для канала", index=False, header=False)
#         df_avg_divergence.to_excel(self.excel_writer, "Отклонение строки от общего", index=False, header=False)
#
#     def save_graphs(self):
#         pass
#
#
# class TaskNoise2_1(BaseAreaTask):
#     """
#     Нахождение линии тренда для каждой строки
#     """
#     task_name = "Шумы 2.1 (линейный тренд)"
#
#     def analyze(self, draw_graphs: bool = False):
#         self.save_excel()
#         self.excel_writer.close()
#         logging.info(f"Шумы 2.1 завершён")
#
#     def save_excel(self):
#         height = self.area.height
#         width = self.area.width
#
#         for channel in range(5, 20):
#             ch_area = self.area.get_vis_channel(channel)
#
#             ch_table = []
#
#             x = np.array(list(range(width)))
#             for i in range(height):
#                 row = ch_area[i]
#                 k, b = utils.linregress(x, row)
#                 trend = x * k + b
#                 ch_table.append([f"Строка {i}"] + row.tolist())
#                 ch_table.append([f"Тренд строки {i}"] + trend.tolist())
#                 ch_table.append([f"Отклонение от тренда"] + (row - trend).tolist())
#                 ch_table.append([])
#
#             df = pd.DataFrame(ch_table)
#             df.to_excel(self.excel_writer, f"Канал {channel}", index=False, header=False)
#
#     def save_graphs(self):
#         pass
#
#
# class TaskNoise2_2(BaseAreaTask):
#     """
#     Нахождение другого тренда, получаемого из среднего по строке, столбцу и общему среднему
#     """
#     task_name = "Шумы 2.2 (тренд по средним)"
#
#     def analyze(self, draw_graphs: bool = False):
#         self.save_excel()
#         self.excel_writer.close()
#         logging.info(f"Шумы 2.2 завершён")
#
#     def save_excel(self):
#         height = self.area.height
#         width = self.area.width
#
#         raw_data_table = []
#         row_excl_table = []
#         col_excl_table = []
#         stds_table = [["Строка"] + [f"Канал {ch}" for ch in range(5, 20)],
#                       ["Std области:", ]]
#         for i in range(height):
#             stds_table.append([i, ])
#
#         for channel in range(5, 20):
#             ch_area = self.area.get_vis_channel(channel)
#
#             raw_data_table.append([f"Канал {channel}", ])
#             raw_data_table += ch_area.tolist()
#             raw_data_table.append([])
#
#             # Вычитаем из строки её отклонение от общего среднего
#             area_avg = ch_area.mean()
#             for i in range(height):
#                 row_avg = ch_area[i].mean()
#                 row_deviation = row_avg - area_avg
#                 ch_area[i] -= row_deviation
#
#             row_excl_table.append([f"Канал {channel}", ])
#             row_excl_table += ch_area.tolist()
#             row_excl_table.append([])
#
#             # Вычитаем из столбца его среднее
#             for j in range(width):
#                 col_avg = ch_area[:, j].mean()
#                 ch_area[:, j] -= col_avg
#
#             col_excl_table.append([f"Канал {channel}", ])
#             col_excl_table += ch_area.tolist()
#             col_excl_table.append([])
#
#             stds_table[1].append(ch_area.std())
#             for i in range(height):
#                 row_std = ch_area[i].std()
#                 stds_table[i + 2].append(row_std)
#
#         pd.DataFrame(raw_data_table).to_excel(self.excel_writer, f"Исходные данные", index=False, header=False)
#         pd.DataFrame(row_excl_table).to_excel(self.excel_writer, f"Вычитание отклонения строки", index=False,
#                                               header=False)
#         pd.DataFrame(col_excl_table).to_excel(self.excel_writer, f"Вычитание среднего столбца", index=False,
#                                               header=False)
#         pd.DataFrame(stds_table).to_excel(self.excel_writer, f"Ст. откл. строк", index=False, header=False)
#
#     def save_graphs(self):
#         pass


AREA_TASKS = [
    Task1,
    Task2,
    Task3,
    Task4,
    Task5,
    TaskNoise1_1,
    # TaskNoise1_2,
    # TaskNoise2_1,
    # TaskNoise2_2,
]
DICT_AREA_TASKS = {task.task_name: task for task in AREA_TASKS}

