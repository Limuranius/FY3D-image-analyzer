import os
from abc import ABC, abstractmethod
import numpy as np
from FY3DImageArea import FY3DImageArea
from FY3DImage import FY3DImage
import vars
import pandas as pd
import utils
import matplotlib.pyplot as plt
import logging
from math import sqrt


class BaseTask(ABC):
    excel_dir: str = "Excel таблицы"
    graphs_dir: str = "Графики"
    root_dir: str
    excel_writer: pd.ExcelWriter
    obj_name: str

    def __init__(self):
        # Создаём обработчика эксель файла
        file_name = self.obj_name + ".xlsx"
        path = os.path.join(self.root_dir, self.excel_dir, file_name)
        utils.create_dirs(path)
        self.excel_writer = pd.ExcelWriter(path)

    @abstractmethod
    def analyze(self, draw_graphs: bool = False):
        pass

    @abstractmethod
    def save_graphs(self, *args, **kwargs):
        pass

    @abstractmethod
    def save_excel(self, *args, **kwargs):
        pass

    def save_figure(self, fig: plt.Figure, fig_name: str):
        """fig_name - название файла без разрешения"""
        fig_dir = os.path.join(self.root_dir, self.graphs_dir, self.obj_name)
        fig_name += ".png"
        fig_path = os.path.join(fig_dir, fig_name)
        utils.create_dirs(fig_path)
        fig.savefig(fig_path)
        plt.close(fig)


class BaseAreaTask(BaseTask, ABC):
    area: FY3DImageArea

    def __init__(self, area: FY3DImageArea):
        self.area = area
        self.obj_name = self.area.name
        super().__init__()


class BaseImageTask(BaseTask, ABC):
    image: FY3DImage

    def __init__(self, image: FY3DImage):
        self.image = image
        self.obj_name = self.image.name
        super().__init__()


class BBTask(BaseImageTask):
    root_dir = vars.BB_DIR

    def analyze(self, draw_graphs: bool = False):
        logging.info(f"Рассматриваем чёрное тело...")
        bb = self.image.BB_DN_average
        self.save_excel(bb)
        if draw_graphs:
            self.save_graphs(bb)
        self.excel_writer.close()

    def save_excel(self, bb: np.ndarray):
        logging.info("Сохраняем чёрное тело в excel-файл")
        df = pd.DataFrame(bb)
        df.to_excel(self.excel_writer, "Чёрное тело")

    def save_graphs(self, bb: np.ndarray):
        logging.info("Создаём графики чёрного тела для каналов:")
        for ch_i in range(25):
            channel_number = ch_i + 1
            logging.info(f"Канал {channel_number}")
            bb_row = bb[ch_i]
            x = list(range(len(bb_row)))
            fig, ax = plt.subplots()
            ax.set_title(f"График среднего значения чёрного тела для 10 строк\nдля канала {channel_number}")
            ax.set_xlabel("Номер десятка строк")
            ax.set_ylabel("Среднее значение чёрного тела по 10 строкам")
            ax.plot(x, bb_row)
            self.save_figure(fig, f"Канал {channel_number}")


class Task1(BaseAreaTask):
    """
    Метод 1.
    Для каждой строки:
        Находим среднее значение - одно число на строку
        Для каждого пикселя находится отклонение от этого среднего
    """
    root_dir = vars.METHOD_1_DIR

    def analyze(self, draw_graphs: bool = False):
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Вычитаем из каждой строки её среднее значение
            for row in range(height):
                row_avg = ch_area[row].mean()
                ch_area[row] -= row_avg

            # Сохраняем значения
            if draw_graphs:
                self.save_graphs(ch_area, channel)
            self.save_excel(self.excel_writer, ch_area, channel)
            logging.info(f"Канал {channel} сохранён")
        self.excel_writer.close()
        logging.info(f"Метод 1 завершён")

    def save_excel(self, excel_writer, ch_area: np.ndarray, channel: int):
        df = pd.DataFrame(ch_area)
        df.to_excel(excel_writer, f"Канал {channel}")

    def save_graphs(self, ch_area: np.ndarray, channel: int):
        fig, ax = plt.subplots()
        ax.set_title(f"График отклонения от среднего по строке для канала {channel}")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Отклонение от среднего по строке")

        height, width = ch_area.shape
        x = list(range(width))
        for i in range(height):
            ax.plot(x, ch_area[i])
        ax.legend(list(range(height)), title="Строка", loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1))

        self.save_figure(fig, f"Канал {channel}")


class Task2(BaseAreaTask):
    """
    Метод 2.
    Для каждого столбца:
        Находим среднее столбца
        Для каждого пикселя находится отклонение от этого среднего
    """
    root_dir = vars.METHOD_2_DIR

    def analyze(self, draw_graphs: bool = False):
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Вычитаем из каждого столбца его среднее значение
            for col in range(width):
                col_avg = ch_area[:, col].mean()
                ch_area[:, col] -= col_avg

            # Сохраняем значения
            if draw_graphs:
                self.save_graphs(ch_area, channel)
            self.save_excel(self.excel_writer, ch_area, channel)
            logging.info(f"Канал {channel} сохранён")
        self.excel_writer.close()
        logging.info(f"Метод 2 завершён")

    def save_excel(self, excel_writer, ch_area: np.ndarray, channel: int):
        df = pd.DataFrame(ch_area)
        df.to_excel(excel_writer, f"Канал {channel}")

    def save_graphs(self, ch_area: np.ndarray, channel: int):
        fig, ax = plt.subplots()
        ax.set_title(f"График отклонения от среднего каждого столбца для канала {channel}")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Отклонение от среднего по столбцу")

        height, width = ch_area.shape
        x = list(range(width))
        for i in range(height):
            ax.plot(x, ch_area[i])
        ax.legend(list(range(height)), title="Строка", loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1))

        self.save_figure(fig, f"Канал {channel}")


class Task3(BaseAreaTask):
    """
    Метод 3.
        У каждого столбца находим среднее и отображаем его на графике
    """
    root_dir = vars.METHOD_3_DIR

    def analyze(self, draw_graphs: bool = False):
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Находим среднее значение каждого столбца
            avg_cols = []
            for col in range(width):
                avg_cols.append(ch_area[:, col].mean())
            avg_cols = np.array(avg_cols)

            # Сохраняем значения
            if draw_graphs:
                self.save_graphs(avg_cols, channel)
            self.save_excel(self.excel_writer, avg_cols, channel)
            logging.info(f"Канал {channel} сохранён")
        self.excel_writer.close()
        logging.info(f"Метод 3 завершён")

    def save_excel(self, excel_writer, avg_cols: np.ndarray, channel: int):
        df = pd.DataFrame(avg_cols)
        df.to_excel(excel_writer, f"Канал {channel}")

    def save_graphs(self, avg_cols: np.ndarray, channel: int):
        fig, ax = plt.subplots()
        ax.set_title(f"График средних значений каждого столбца для канала {channel}")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Среднее значение")

        width = self.area.width
        x = list(range(width))
        ax.plot(x, avg_cols)

        self.save_figure(fig, f"Канал {channel}")


class Task4(BaseAreaTask):
    """
    Метод 4.
        У каждого столбца находим стандартное отклонение и отображаем его на графике
    """
    root_dir = vars.METHOD_4_DIR

    def analyze(self, draw_graphs: bool = False):
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            height, width = ch_area.shape

            # Находим стандартное отклонение каждого столбца
            stds = []
            for col in range(width):
                stds.append(ch_area[:, col].std())
            stds = np.array(stds)

            # Сохраняем значения
            if draw_graphs:
                self.save_graphs(stds, channel)
            self.save_excel(self.excel_writer, stds, channel)
            logging.info(f"Канал {channel} сохранён")
        self.excel_writer.close()
        logging.info(f"Метод 4 завершён")

    def save_excel(self, excel_writer, stds: np.ndarray, channel: int):
        df = pd.DataFrame(stds)
        df.to_excel(excel_writer, f"Канал {channel}")

    def save_graphs(self, stds: np.ndarray, channel: int):
        fig, ax = plt.subplots()
        ax.set_title(f"График стандартного отклонения каждого столбца для канала {channel}")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Стандартное отклонение")

        width = self.area.width
        x = list(range(width))
        ax.plot(x, stds)

        self.save_figure(fig, f"Канал {channel}")


class Task5(BaseAreaTask):
    """
    Метод 5.
        Находим среднее по всей области
        У каждого пикселя находим отклонение от этого среднего
    """
    root_dir = vars.METHOD_5_DIR

    def analyze(self, draw_graphs: bool = False):
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)

            # Находим отклонение каждого пикселя от общего среднего
            avg = ch_area.mean()
            ch_area -= avg

            # Сохраняем значения
            if draw_graphs:
                self.save_graphs(ch_area, channel)
            self.save_excel(self.excel_writer, ch_area, channel)
            logging.info(f"Канал {channel} сохранён")
        self.excel_writer.close()
        logging.info(f"Метод 5 завершён")

    def save_excel(self, excel_writer, ch_area: np.ndarray, channel: int):
        df = pd.DataFrame(ch_area)
        df.to_excel(excel_writer, f"Канал {channel}")

    def save_graphs(self, ch_area: np.ndarray, channel: int):
        fig, ax = plt.subplots()
        ax.set_title(f"График отклонения от общего среднего для каждой строки\nдля канала {channel}")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Отклонение от общего среднего")

        height, width = ch_area.shape
        x = list(range(width))
        for i in range(height):
            ax.plot(x, ch_area[i])
        ax.legend(list(range(height)), title="Строка", loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1))

        self.save_figure(fig, f"Канал {channel}")


class TaskNoise1_1(BaseAreaTask):
    """
    Нахождение среднего, стандартного отклонения и случайной ошибки каждой строки
    """
    root_dir = vars.NOISES_1_1_DIR

    def analyze(self, draw_graphs: bool = False):
        self.save_excel()
        self.excel_writer.close()
        logging.info(f"Шумы 1.1 завершён")

    def save_excel(self):
        height = self.area.height

        # Таблицы с заполненными заголовками
        std_table = [["Строка"] + [f"{ch} канал" for ch in range(5, 20)],
                     ["Std области: ", ]]
        error_table = [["Строка"] + [f"{ch} канал" for ch in range(5, 20)]]
        avg_table = [["Строка"] + [f"{ch} канал" for ch in range(5, 20)]]

        for i in range(height):
            std_table.append([i, ])
            error_table.append([i, ])
            avg_table.append([i, ])

        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            std_table[1].append(ch_area.std())
            for i in range(height):
                row = ch_area[i]
                row_std = row.std()
                row_avg = row.mean()
                row_error = row_std / sqrt(len(row))
                std_table[i + 2].append(row_std)
                error_table[i + 1].append(row_error)
                avg_table[i + 1].append(row_avg)
        df_std = pd.DataFrame(std_table)
        df_error = pd.DataFrame(error_table)
        df_avg = pd.DataFrame(avg_table)
        df_std.to_excel(self.excel_writer, "Стандартное отклонение", index=False, header=False)
        df_error.to_excel(self.excel_writer, "Случайная ошибка", index=False, header=False)
        df_avg.to_excel(self.excel_writer, "Среднее значение", index=False, header=False)

    def save_graphs(self):
        pass


class TaskNoise1_2(BaseAreaTask):
    """
    Нахождение стандартного отклонения и случайной ошибки для всей области
    Нахождение общего среднего области и отклонения среднего каждой строки от этого общего среднего
    """
    root_dir = vars.NOISES_1_2_DIR

    def analyze(self, draw_graphs: bool = False):
        self.save_excel()
        self.excel_writer.close()
        logging.info(f"Шумы 1.2 завершён")

    def save_excel(self):
        height = self.area.height
        width = self.area.width

        # Таблицы с заполненными заголовками
        ch_std_table = [["Канал", "Стандартное отклонение", "Случайная ошибка"]]
        avg_divergence_table = [["Строка"] + [f"{ch} канал" for ch in range(5, 20)],
                                ["Среднее области", ]]
        for i in range(height):
            avg_divergence_table.append([i, ])

        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            area_std = ch_area.std()
            area_avg = ch_area.mean()
            area_error = area_std / sqrt(height * width)

            ch_std_table.append([channel, area_std, area_error])
            avg_divergence_table[1].append(area_avg)

            for i in range(height):
                row = ch_area[i]
                row_avg = row.mean()
                avg_divergence_table[i + 2].append(row_avg - area_avg)

        df_ch_std = pd.DataFrame(ch_std_table)
        df_avg_divergence = pd.DataFrame(avg_divergence_table)
        df_ch_std.to_excel(self.excel_writer, "Std и случ. ошибка для канала", index=False, header=False)
        df_avg_divergence.to_excel(self.excel_writer, "Отклонение строки от общего", index=False, header=False)

    def save_graphs(self):
        pass


class TaskNoise2_1(BaseAreaTask):
    """
    Нахождение линии тренда для каждой строки
    """
    root_dir = vars.NOISES_2_1_DIR

    def analyze(self, draw_graphs: bool = False):
        self.save_excel()
        self.excel_writer.close()
        logging.info(f"Шумы 2.1 завершён")

    def save_excel(self):
        height = self.area.height
        width = self.area.width

        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)

            ch_table = []

            x = np.array(list(range(width)))
            for i in range(height):
                row = ch_area[i]
                k, b = utils.linregress(x, row)
                trend = x * k + b
                ch_table.append([f"Строка {i}"] + row.tolist())
                ch_table.append([f"Тренд строки {i}"] + trend.tolist())
                ch_table.append([f"Отклонение от тренда"] + (row - trend).tolist())
                ch_table.append([])

            df = pd.DataFrame(ch_table)
            df.to_excel(self.excel_writer, f"Канал {channel}", index=False, header=False)

    def save_graphs(self):
        pass


class TaskNoise2_2(BaseAreaTask):
    """
    Нахождение другого тренда, получаемого из среднего по строке, столбцу и общему среднему
    """
    root_dir = vars.NOISES_2_2_DIR

    def analyze(self, draw_graphs: bool = False):
        self.save_excel()
        self.excel_writer.close()
        logging.info(f"Шумы 2.2 завершён")

    def save_excel(self):
        height = self.area.height
        width = self.area.width

        raw_data_table = []
        row_excl_table = []
        col_excl_table = []
        stds_table = [["Строка"] + [f"Канал {ch}" for ch in range(5, 20)],
                      ["Std области:", ]]
        for i in range(height):
            stds_table.append([i, ])

        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)

            raw_data_table.append([f"Канал {channel}", ])
            raw_data_table += ch_area.tolist()
            raw_data_table.append([])

            # Вычитаем из строки её отклонение от общего среднего
            area_avg = ch_area.mean()
            for i in range(height):
                row_avg = ch_area[i].mean()
                row_deviation = row_avg - area_avg
                ch_area[i] -= row_deviation

            row_excl_table.append([f"Канал {channel}", ])
            row_excl_table += ch_area.tolist()
            row_excl_table.append([])

            # Вычитаем из столбца его среднее
            for j in range(width):
                col_avg = ch_area[:, j].mean()
                ch_area[:, j] -= col_avg

            col_excl_table.append([f"Канал {channel}", ])
            col_excl_table += ch_area.tolist()
            col_excl_table.append([])

            stds_table[1].append(ch_area.std())
            for i in range(height):
                row_std = ch_area[i].std()
                stds_table[i + 2].append(row_std)

        pd.DataFrame(raw_data_table).to_excel(self.excel_writer, f"Исходные данные", index=False, header=False)
        pd.DataFrame(row_excl_table).to_excel(self.excel_writer, f"Вычитание отклонения строки", index=False, header=False)
        pd.DataFrame(col_excl_table).to_excel(self.excel_writer, f"Вычитание среднего столбца", index=False, header=False)
        pd.DataFrame(stds_table).to_excel(self.excel_writer, f"Ст. откл. строк", index=False, header=False)

    def save_graphs(self):
        pass