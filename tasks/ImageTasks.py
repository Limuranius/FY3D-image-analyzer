from .BaseTasks import *
from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
import logging
from utils.save_data_utils import save_excel, create_and_save_figure
import numpy as np
from utils.Table import Table
from utils.area_utils import filter_areas_by_mirror_side
from vars import KMIRROR_SIDE


class BaseImageTask(BaseTask, ABC):
    image: FY3DImage

    def __init__(self, image: FY3DImage):
        self.image = image
        self.obj_name = self.image.name
        super().__init__()

    def get_areas(self) -> list[FY3DImageArea]:
        return self.image.areas


class BBTask(BaseImageTask):
    """Просмотр яркости чёрного тела для разных каналов"""
    task_name = "Чёрное тело"

    def calculate_data(self):
        logging.info(f"Рассматриваем чёрное тело...")
        bb = self.image.BB_DN_average
        return bb

    def save_excel(self, bb: np.ndarray):
        sheets = [
            ("Чёрное тело", bb)
        ]
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)

    def save_graphs(self, bb: np.ndarray):
        logging.info("Создаём графики чёрного тела для каналов:")
        min_bb = bb[0:19].min()
        max_bb = bb[0:19].max()
        for ch_i in range(19):
            channel_number = ch_i + 1
            logging.info(f"Канал {channel_number}")
            bb_row = bb[ch_i]
            x = list(range(len(bb_row)))
            path = self.get_graph_img_path(f"Канал {channel_number}")
            create_and_save_figure(path, [bb_row], [x],
                                   title=f"График среднего значения чёрного тела для 10 строк\nдля канала {channel_number}",
                                   xlabel="Номер десятка строк", ylabel="Среднее значение чёрного тела по 10 строкам",
                                   lim=(min_bb, max_bb))


# TODO: Переделать под новый код
# class TaskNoise3_1(KMirrorBaseTask):
#     """
#     Проверка K-зеркала путём сравнения показаний одинаковых датчиков на областях, расположенных друг под другом таких,
#     что первая область получена одной стороной зеркала, а вторая - другой
#     Метод:
#         Имеем две области, расположенные друг под другом.
#         Находим средние по строкам;
#         Для обеих областей находим размах (разницу между максимальным и минимальным средним по строке) и сравниваем их
#
#         Дополнительно выводим ст. отклонение и случайную ошибку для строк
#     """
#     task_name = "Шумы 3 (K-зеркало)"
#
#     def analyze(self, draw_graphs: bool = False):
#         self.save_excel()
#         self.excel_writer.close()
#         logging.info(f"Шумы 3 завершён")
#
#     def save_excel(self):
#         pairs = self.find_neighbor_areas()
#
#         header = ["Строка"] + [f"{ch} канал" for ch in range(5, 20)]
#
#         for higher_area, lower_area in pairs:
#             width, height = higher_area.width, higher_area.height
#
#             high_avg_table = [[i, ] for i in range(height)]
#             low_avg_table = [[i, ] for i in range(height)]
#
#             high_range_table = ["", ]
#             low_range_table = ["", ]
#
#             high_std_table = [[i, ] for i in range(height)]
#             low_std_table = [[i, ] for i in range(height)]
#
#             high_error_table = [[i, ] for i in range(height)]
#             low_error_table = [[i, ] for i in range(height)]
#
#             for channel in range(5, 20):
#                 high_ch_area = higher_area.get_vis_channel(channel)
#                 low_ch_area = lower_area.get_vis_channel(channel)
#
#                 for i in range(height):
#                     high_row_avg = high_ch_area[i].mean()
#                     low_row_avg = low_ch_area[i].mean()
#
#                     high_row_std = high_ch_area[i].std()
#                     low_row_std = low_ch_area[i].std()
#
#                     high_row_error = high_ch_area[i].std() / sqrt(len(high_ch_area[i]))
#                     low_row_error = low_ch_area[i].std() / sqrt(len(low_ch_area[i]))
#
#                     high_avg_table[i].append(high_row_avg)
#                     low_avg_table[i].append(low_row_avg)
#                     high_std_table[i].append(high_row_std)
#                     low_std_table[i].append(low_row_std)
#                     high_error_table[i].append(high_row_error)
#                     low_error_table[i].append(low_row_error)
#
#             # Подсчитываем размах средних по строке для нижней и верхней областей
#             for channel in range(5, 20):
#                 j = channel - 5 + 1
#                 high_avg_col = [high_avg_table[i][j] for i in range(height)]
#                 low_avg_col = [low_avg_table[i][j] for i in range(height)]
#
#                 high_range_table.append(max(high_avg_col) - min(high_avg_col))
#                 low_range_table.append(max(low_avg_col) - min(low_avg_col))
#
#             result_table = [
#                 ["Зеркало 1"],
#                 header,
#                 *high_avg_table,
#                 [],
#                 ["Зеркало 2"],
#                 header,
#                 *low_avg_table,
#                 [],
#                 ["Размах"],
#                 high_range_table,
#                 low_range_table,
#                 [],
#                 ["Стандартное отклонение, зеркало 1"],
#                 *high_std_table,
#                 [],
#                 ["Стандартное отклонение, зеркало 2"],
#                 *low_std_table,
#                 [],
#                 ["Случайная ошибка, зеркало 1"],
#                 *high_error_table,
#                 [],
#                 ["Случайная ошибка, зеркало 2"],
#                 *low_error_table,
#                 [],
#             ]
#             sheet_name = f"{higher_area.x} {higher_area.y}"
#             pd.DataFrame(result_table).to_excel(self.excel_writer, sheet_name, index=False, header=False)
#
#     def save_graphs(self):
#         pass
#
#
# class KMirror1(KMirrorBaseTask):
#     """Выводит графики областей двустороннего зеркала"""
#     task_name = "К-зеркало 1"
#
#     def analyze(self, draw_graphs: bool = False):
#         self.save_excel()
#         self.excel_writer.close()
#         if draw_graphs:
#             self.save_graphs()
#
#     def save_excel(self):
#         for higher, lower in self.find_neighbor_areas():
#             header = [""] + [f"Канал {i}" for i in range(5, 20)]
#             area_data_table = [
#                 ["Первое"],
#                 ["Второе"],
#                 ["Разница"],
#                 ["Стандартное отклонение области"]
#             ]
#             for ch in range(5, 20):
#                 h_area = higher.get_vis_channel(ch)
#                 l_area = lower.get_vis_channel(ch)
#                 both_area = np.concatenate((h_area, l_area))
#
#                 area_data_table[0].append(h_area.mean())
#                 area_data_table[1].append(l_area.mean())
#                 area_data_table[2].append(h_area.mean() - l_area.mean())
#                 area_data_table[3].append(both_area.std())
#
#             table = [
#                 header,
#                 *area_data_table,
#             ]
#             sheet_name = f"x={higher.x} y={higher.y} w={higher.width} h={higher.height}"
#             pd.DataFrame(table).to_excel(self.excel_writer, sheet_name, index=False, header=False)
#
#     def save_graphs(self):
#         for higher, lower in self.find_neighbor_areas():
#             width = higher.width
#             for ch in range(5, 20):
#                 h_area = higher.get_vis_channel(ch)
#                 l_area = lower.get_vis_channel(ch)
#
#                 h_col_avg = []
#                 l_col_avg = []
#
#                 for col in range(width):
#                     h_col_avg.append(h_area[:, col].mean())
#                     l_col_avg.append(l_area[:, col].mean())
#
#                 self.create_and_save_figure(
#                     [h_col_avg, l_col_avg], f"Канал {ch} {higher.x} {higher.y}",
#                     title=f"Средние значения столбцов для двух сторон зеркала\nна канале {ch}",
#                     xlabel="Номер столбца", ylabel="Среднее значение столбца", legend_title="Сторона зеркала",
#                     legend=["Первая", "Вторая"]
#                 )
#
#
# class KMirrorRawData(KMirrorBaseTask):
#     """Получение изначальных данных"""
#     task_name = "Сырые данные K-зеркал"
#
#     def analyze(self, draw_graphs: bool = False):
#         logging.info("Получаем сырые значения K-зеркал...")
#         self.save_excel()
#         self.excel_writer.close()
#         if draw_graphs:
#             self.save_graphs()
#         logging.info("Готово!")
#
#     def save_excel(self):
#         for higher, lower in self.find_neighbor_areas():
#             table = []
#
#             for ch in range(5, 20):
#                 h_area = higher.get_vis_channel(ch)
#                 l_area = lower.get_vis_channel(ch)
#
#                 table.append([f"Верхняя область, канал {ch}"])
#                 table += h_area.tolist()
#                 table.append([])
#                 table.append([f"Нижняя область, канал {ch}"])
#                 table += l_area.tolist()
#                 table += [[], [], []]
#             sheet_name = f"x={higher.x} y={higher.y} w={higher.width} h={higher.height}"
#             pd.DataFrame(table).to_excel(self.excel_writer, sheet_name, index=False, header=False)
#
#     def save_graphs(self):
#         pass
#
#
# class ImageVisualTask:
#     task_name: str
#     root_dir: str  # Папка, куда можно скидывать всякую всячину по текущей задаче
#     image: FY3DImage
#     task_name = "Различие зеркал в столбце"
#
#     def __init__(self, image: FY3DImage):
#         self.image = image
#         self.root_dir = os.path.join(vars.RESULTS_DIR, self.task_name, self.image.name)
#         utils.create_dirs(self.root_dir)
#
#     def analyze(self, draw_graphs: bool = False):
#         logging.info("Рисуем различие зеркал в областях:")
#         pairs = find_neighbor_areas(self.image.areas)
#         for ch in range(5, 20):
#             img = self.image.get_colored_picture()
#             for high_area, low_area in pairs:
#                 self.process_area(high_area, low_area, img, ch)
#             f_name = f"Канал {ch}.png"
#             f_path = os.path.join(self.root_dir, f_name)
#             img.save(f_path)
#             logging.info(f"\tКанал {ch} готов")
#
#     def process_area(self, high_area: FY3DImageArea, low_area: FY3DImageArea, image: Image, channel: int):
#         high_arr = high_area.get_vis_channel(channel)
#         low_arr = low_area.get_vis_channel(channel)
#         both_arr = np.concatenate((high_arr, low_arr))
#         both_std = both_arr.std()
#         pixels = image.load()
#
#         height, width = high_arr.shape
#
#         # Вычитаем средние по столбцам
#         for col in range(width):
#             high_col = high_arr[:, col]
#             low_col = low_arr[:, col]
#             both_avg = np.concatenate(low_col, high_col).mean()
#             high_arr[:, col] -= both_avg
#             low_arr[:, col] -= both_avg
#
#         # both_arr = np.concatenate((high_arr, low_arr))
#         # both_std = both_arr.std()
#         #
#         # for col in range(width):
#         #     high_col = high_arr[:, col]
#         #     low_col = low_arr[:, col]
#         #     high_avg = high_col.mean()
#         #     low_avg = low_col.mean()
#         #     diff = high_avg - low_avg
#         #     if diff < both_std:
#         #         color = (0, 255, 0)  # Зелёный
#         #     elif both_std <= diff < 2 * both_std:
#         #         color = (255, 255, 0)  # Жёлтый
#         #     else:
#         #         color = (255, 0, 0)  # Красный
#         #
#         #     # Закрашиваем столбец в соответствующий цвет
#         #     for i in range(height * 2):
#         #         x, y = high_area.get_global_coords(col, i)
#         #         pixels[x, y] = color
#
#         for col in range(width):
#             high_col = high_arr[:, col]
#             low_col = low_arr[:, col]
#             high_avg = high_col.mean()
#             low_avg = low_col.mean()
#             diff = high_avg - low_avg
#             if diff < both_std:
#                 color = (0, 255, 0)  # Зелёный
#             elif both_std <= diff < 2 * both_std:
#                 color = (255, 255, 0)  # Жёлтый
#             else:
#                 color = (255, 0, 0)  # Красный
#
#             # Закрашиваем столбец в соответствующий цвет
#             for i in range(height * 2):
#                 x, y = high_area.get_global_coords(col, i)
#                 pixels[x, y] = color
#
#
# class SensorSystemErrorTask(BaseImageTask):
#     """
#     Находит отклонение среднего по датчику от среднего по области
#     и расфасовывает данные по номеру датчика
#     """
#     task_name = "Систематическая ошибка сенсоров"
#
#     def analyze(self, draw_graphs: bool = False):
#         self.save_excel()
#         self.excel_writer.close()
#
#     def save_excel(self, data):
#         header = ["Области"] + [f"Канал {i}" for i in range(5, 20)]
#         for sensor_i in range(10):
#             table_data = []
#             col_avg = ["Среднее:"]
#             for area in self.image.areas:
#                 table_row = [area.get_short_name()]
#                 std_row = ["std"]
#                 for ch in range(5, 20):
#                     ch_area = area.get_vis_channel(ch)
#                     ch_area_avg = ch_area.mean()
#                     curr_sensor_row_avg = ch_area[sensor_i].mean()
#                     table_row.append(curr_sensor_row_avg - ch_area_avg)
#                     std_row.append(ch_area.std())
#                 table_data.append(table_row)
#                 table_data.append(std_row)
#                 table_data.append([])
#             # Находим средние по столбцам
#             for j in range(1, 16):
#                 s = 0
#                 for i in range(0, len(table_data), 3):
#                     s += table_data[i][j]
#                 col_avg.append(s / len(table_data))
#             table = [
#                 # [f"Разница между датчиком {sensor_i} и эталонным датчиком {reference_sensor}"],
#                 [f"Разница между датчиком {sensor_i} и средним области"],
#                 header,
#                 *table_data,
#                 [],
#                 col_avg
#             ]
#             pd.DataFrame(table).to_excel(self.excel_writer, f"Датчик {sensor_i}", index=False, header=False)


class SensorSystemErrorTask2(BaseImageTask):
    """
    Находит отклонение среднего по датчику от среднего по области
    и расфасовывает данные по номеру канала
    Формат data:
    (
        Канал,
        [][] Отклонения датчиков в областях
        [] Средние значения столбцов (т. е. средние отклонения датчиков)
        [] Средние по модулю значения столбцов
    )
    """
    task_name = "Систематическое отклонение сенсоров"

    def get_areas(self) -> list[FY3DImageArea]:
        return filter_areas_by_mirror_side(self.image.areas, KMIRROR_SIDE)

    def calculate_data(self):
        areas = self.get_areas()
        data = []
        for ch in range(5, 20):
            h = len(areas)
            w = 10
            deviations = np.ndarray((h, w), np.float64)
            for area_i, area in enumerate(areas):
                ch_area = area.get_vis_channel(ch)
                ch_area_avg = ch_area.mean()
                for sensor_i in range(0, 10):
                    sensor_avg = ch_area[sensor_i].mean()
                    deviations[area_i, sensor_i] = sensor_avg - ch_area_avg

            # Находим средние по столбцам отклонений
            cols_avg = []
            cols_abs_avg = []
            for j in range(0, 10):
                col = deviations[:, j]
                cols_avg.append(col.mean())
                cols_abs_avg.append(np.abs(col).mean())
            data.append((
                ch,
                deviations.tolist(),
                cols_avg,
                cols_abs_avg
            ))
        return data

    def save_excel(self, data):
        sheets = []
        for ch_data in data:
            ch, deviations, cols_avg, cols_abs_avg = ch_data
            hh = ["Область"] + [f"Датчик {i}" for i in range(0, 10)]
            vh = [area.get_short_name() for area in self.get_areas()] + ["Среднее:", "Среднее по модулю:"]
            t = Table(horiz_head=hh, vert_head=vh)
            for area_deviations in deviations:
                t.append_row(area_deviations)
            t.append_row(cols_avg)
            t.append_row(cols_abs_avg)
            sheets.append((
                f"Канал {ch}",
                t.get_content()
            ))
        path = self.get_excel_path(self.obj_name)
        save_excel(path, sheets)


IMAGE_TASKS = [
    BBTask,
    # TaskNoise3_1,
    # KMirror1,
    # ImageVisualTask,
    # KMirrorRawData,
    # SensorSystemErrorTask,
    SensorSystemErrorTask2,
]
DICT_IMAGE_TASKS = {task.task_name: task for task in IMAGE_TASKS}
