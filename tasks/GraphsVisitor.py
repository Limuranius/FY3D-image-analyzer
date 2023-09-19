from tasks.BaseVisitor import *
import vars
import os
from scipy.stats import linregress
from utils.save_data_utils import create_and_save_figure
import tqdm
import numpy as np


def get_graphs_path_and_create(task, file_name: str, inner_dir: str = ""):
    """Для таски task находит путь файла для графика, создаёт его и возвращает
    inner_dir: Путь внутри папки графиков таски. Например, если надо выделить папку для каждого снимка
    """
    graphs_dir_path = os.path.join(vars.RESULTS_DIR, task.task_name, "Графики")
    path = os.path.join(graphs_dir_path, inner_dir)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, file_name)
    if not file_path.endswith(".png"):
        file_path += ".png"
    return file_path


class GraphsVisitor(BaseVisitor):

    def visit_AreaSensorMeanRowDeviation(self, task: AreaTasks.SensorMeanRowDeviation):
        data = task.result
        for channel in range(5, 20):
            x_rows = []
            y_rows = []
            for sens_i in range(10):
                x = list(range(100))
                y = data.loc[(data["channel"] == channel) & (data["sens_i"] == sens_i), "deviations"].item()
                x_rows.append(x)
                y_rows.append(y)

            path = get_graphs_path_and_create(task, f"Канал {channel}",
                                              inner_dir=os.path.join(task.area.image.get_unique_name(),
                                                                     task.area.get_short_name()))
            create_and_save_figure(path, y_rows, x_rows=x_rows,
                                   title=f"График отклонения от среднего по строке для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Отклонение от среднего по строке",
                                   legend=list(range(10)), legend_title="Строка")

    def visit_AreaSensorMeanColumnDeviation(self, task: AreaTasks.SensorMeanColumnDeviation):
        data = task.result
        for channel in range(5, 20):
            x_rows = []
            y_rows = []
            for sens_i in range(10):
                x = list(range(100))
                y = data.loc[(data["channel"] == channel) & (data["sens_i"] == sens_i), "deviations"].item()
                x_rows.append(x)
                y_rows.append(y)
            path = get_graphs_path_and_create(task, f"Канал {channel}",
                                              inner_dir=os.path.join(task.area.image.get_unique_name(),
                                                                     task.area.get_short_name()))
            create_and_save_figure(path, y_rows, x_rows=x_rows,
                                   title=f"График отклонения от среднего каждого столбца для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Отклонение от среднего по столбцу",
                                   legend=list(range(10)), legend_title="Строка")

    def visit_AreaAreaMean(self, task: AreaTasks.AreaMean):
        data = task.result
        for _, row in data.iterrows():
            channel = row["channel"]
            avg_cols = row["values"]
            path = get_graphs_path_and_create(task, f"Канал {channel}", inner_dir=os.path.join(
                task.area.image.get_unique_name(),
                task.area.get_short_name()))
            create_and_save_figure(path, [avg_cols],
                                   title=f"График средних значений каждого столбца для канала {channel}",
                                   xlabel="Номер столбца", ylabel="Среднее значение")

    def visit_ImageBBTask(self, task: ImageTasks.BBTask):
        data = task.result
        min_bb = data["dataBB"].apply(np.min).min()
        max_bb = data["dataBB"].apply(np.max).max()
        all_rows = []
        for _, row in data.iterrows():
            channel_number = row["channel"]
            bb_data = row["dataBB"]
            path = get_graphs_path_and_create(task, f"Канал {row['channel']}", inner_dir=task.image.get_unique_name())
            create_and_save_figure(path, [bb_data], None,
                                   title=f"График среднего значения чёрного тела для 10 строк\nдля канала {channel_number}",
                                   xlabel="Номер десятка строк", ylabel="Среднее значение чёрного тела по 10 строкам",
                                   lim=(min_bb, max_bb))
            all_rows.append(bb_data)

        path = get_graphs_path_and_create(task, f"Все каналы", inner_dir=task.image.get_unique_name())
        create_and_save_figure(path, all_rows, None,
                               title=f"График среднего значения чёрного тела для 10 строк\nдля каналов 1 - 19",
                               xlabel="Номер десятка строк", ylabel="Среднее значение чёрного тела по 10 строкам")

    def visit_ImageSVTask(self, task: ImageTasks.SVTask):
        data = task.result
        min_sv = data["dataSV"].apply(np.min).min()
        max_sv = data["dataSV"].apply(np.max).max()
        for _, row in data.iterrows():
            channel_number = row["channel"]
            sv_data = row["dataSV"]
            x = list(range(len(sv_data)))
            path = get_graphs_path_and_create(task, task.image.get_unique_name(), inner_dir=f"Канал {channel_number}")
            create_and_save_figure(path, [sv_data], [x],
                                   title=f"График среднего значения Space View для 10 строк\nдля канала {channel_number}",
                                   xlabel="Номер десятка строк", ylabel="Среднее значение чёрного тела по 10 строкам",
                                   lim=(min_sv, max_sv))

    def visit_RegressByYear(self, task: MultipleImagesTasks.RegressByYear):
        data = task.result
        years = data["year"].unique().tolist()
        years.sort()

        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (RegressByYear)") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    path = get_graphs_path_and_create(task, f"Датчик {sensor_i}", inner_dir=f"Канал {channel}")
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
                    pbar.update(1)

    def visit_DeviationsMeanPerImage(self, task: MultipleImagesTasks.DeviationsMeanPerImage):
        data = task.result
        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (DeviationsMeanPerImage)") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    path = get_graphs_path_and_create(task, f"Датчик {sensor_i}", inner_dir=f"Канал {channel}")

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
                    pbar.update(1)

    def visit_DeviationsByMirrorSide(self, task: MultipleImagesTasks.DeviationsByMirrorSide):
        data = task.result
        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (DeviationsByMirrorSide)") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    path = get_graphs_path_and_create(task, f"Датчик {sensor_i}", inner_dir=f"Канал {channel}")

                    # Фильтруем данные по каналу и датчику
                    filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                    ch_sens_data = data.loc[filt]

                    # Фильтруем данные по стороне зеркала
                    filt_side_1 = ch_sens_data["mirror_side"] == vars.KMirrorSide.SIDE_1
                    filt_side_2 = ch_sens_data["mirror_side"] == vars.KMirrorSide.SIDE_2
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
                                           xlabel="Яркость", ylabel="Отклонение датчика",
                                           fmt_list=[".", ".", "--", "--"],
                                           legend_title="Сторона зеркала",
                                           legend=["Первая", "Вторая", "Первая", "Вторая"])
                    pbar.update(1)

    def visit_DeviationsBySurface(self, task: MultipleImagesTasks.DeviationsBySurface):
        data = task.result
        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (DeviationsBySurface)") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    file_name = f"Датчик {sensor_i}.png"
                    path = get_graphs_path_and_create(task, file_name, inner_dir=f"Канал {channel}")
                    filt = (data["channel"] == channel) & (data["sensor_i"] == sensor_i)
                    ch_sens_data = data.loc[filt]
                    filt_sea = ch_sens_data["surface_type"] == vars.SurfaceType.SEA
                    filt_snow = ch_sens_data["surface_type"] == vars.SurfaceType.SNOW
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
                    pbar.update(1)

    def visit_DeviationsLinearRegression(self, task: MultipleImagesTasks.DeviationsLinearRegression):
        data = task.result
        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (DeviationsLinearRegression)") as pbar:
            for channel in range(5, 20):
                for sensor_i in range(10):
                    path = get_graphs_path_and_create(task, f"Датчик {sensor_i}", inner_dir=f"Канал {channel}")
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
                    pbar.update(1)