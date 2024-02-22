import matplotlib.pyplot as plt

from tasks.BaseVisitor import *
import vars
import os
from scipy.stats import linregress
from utils.save_data_utils import create_and_save_figure
import tqdm
from tqdm import trange
import numpy as np
from database import Deviations
from vars import SurfaceType, KMirrorSide
import seaborn as sns


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
        data = task.get_data()
        min_bb = data["dataBB"].apply(np.min).min()
        max_bb = data["dataBB"].apply(np.max).max()
        all_rows = []
        for _, row in data.iterrows():
            channel_number = row["channel"]
            bb_data = row["dataBB"]
            # path = get_graphs_path_and_create(task, f"Канал {row['channel']}", inner_dir=task.image.get_unique_name())

            if channel_number not in [8, 9, 10]:
                continue
            path = get_graphs_path_and_create(task,
                                              # task.image.get_unique_name(),
                                              str(task.image.id),
                                              inner_dir=f"Канал {row['channel']}")
            lims = {
                8: [140, 160],
                9: [130, 145],
                10: [90, 120]
            }

            create_and_save_figure(path, [bb_data], None,
                                   title=f"График среднего значения чёрного тела для 10 строк\nдля канала {channel_number}",
                                   xlabel="Номер десятка строк", ylabel="Среднее значение чёрного тела по 10 строкам",
                                   # ylim=(min_bb, max_bb)
                                   ylim=lims[channel_number]
                                   )
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
                                   ylim=(min_sv, max_sv))

    def visit_RegressByYear(self, task: DatabaseTasks.RegressByYear):
        data = task.get_data()
        ranges = data["ranges"]
        with tqdm.tqdm(desc="Saving graphs (RegressByYear)", total=150) as pbar:
            for channel in range(5, 20):
                _, x_min, x_max, y_min, y_max = ranges[ranges.CHANNEL == channel].squeeze()
                for sensor in range(10):
                    sensor_data = Deviations.get_dataframe(channel=channel, sensor=sensor)
                    plot = sns.lmplot(data=sensor_data, x="area_avg", y="deviation", hue="year",
                                      scatter_kws=dict(s=1), scatter=True)
                    plot.set(ylim=[y_min, y_max])
                    plot.fig.suptitle(
                        f"Зависимость отклонения датчика от ср. яркости области\n(Канал {channel} датчик {sensor})")
                    path = get_graphs_path_and_create(task, f"Датчик {sensor}", inner_dir=f"Канал {channel}")
                    plot.fig.savefig(path, dpi=300)
                    pbar.update(1)

    def visit_DeviationsByMirrorSide(self, task: DatabaseTasks.DeviationsByMirrorSide):
        data = task.get_data()
        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (DeviationsByMirrorSide)") as pbar:
            for channel in range(5, 20):
                # ch_data = Deviations.get_dataframe(year=2023, channel=channel)
                ch_data = data[data["channel"] == channel]
                xlim = (ch_data["area_avg"].min(), ch_data["area_avg"].max())
                ylim = (ch_data["deviation"].min(), ch_data["deviation"].max())
                for sensor_i in range(10):
                    path = get_graphs_path_and_create(task, f"Датчик {sensor_i}", inner_dir=f"Канал {channel}")

                    # Фильтруем данные по каналу и датчику
                    # ch_sens_data = Deviations.get_dataframe(year=2023, channel=channel, sensor=sensor_i)
                    ch_sens_data = ch_data.loc[ch_data["sensor"] == sensor_i]

                    # Фильтруем данные по стороне зеркала
                    filt_side_1 = ch_sens_data["k_mirror_side"] == vars.KMirrorSide.SIDE_1.value
                    filt_side_2 = ch_sens_data["k_mirror_side"] == vars.KMirrorSide.SIDE_2.value
                    side_1_data = ch_sens_data.loc[filt_side_1]
                    side_2_data = ch_sens_data.loc[filt_side_2]
                    x_side_1 = side_1_data["area_avg"].to_numpy()
                    y_side_1 = side_1_data["deviation"].to_numpy()
                    x_side_2 = side_2_data["area_avg"].to_numpy()
                    y_side_2 = side_2_data["deviation"].to_numpy()

                    # Находим линии регрессии для первого и второго зеркала
                    linreg_side_1 = linregress(x_side_1.astype(float), y_side_1.astype(float))
                    linreg_side_2 = linregress(x_side_2.astype(float), y_side_2.astype(float))
                    slope_side_1, intercept_side_1 = linreg_side_1.slope, linreg_side_1.intercept
                    slope_side_2, intercept_side_2 = linreg_side_2.slope, linreg_side_2.intercept
                    line_x0_side_1 = x_side_1.min()
                    line_x1_side_1 = x_side_1.max()
                    line_y0_side_1 = line_x0_side_1 * slope_side_1 + intercept_side_1
                    line_y1_side_1 = line_x1_side_1 * slope_side_1 + intercept_side_1
                    line_x0_side_2 = x_side_2.min()
                    line_x1_side_2 = x_side_2.max()
                    line_y0_side_2 = line_x0_side_2 * slope_side_2 + intercept_side_2
                    line_y1_side_2 = line_x1_side_2 * slope_side_2 + intercept_side_2

                    significance = 0.05
                    text = f"""Первое зеркало:
Количество = {len(side_1_data)}
Среднее={y_side_1.mean()}
Ст. откл={y_side_1.std()}
slope={slope_side_1} 
slope_stderr={linreg_side_1.stderr}
intercept={intercept_side_1} 
intercept_stderr={linreg_side_1.intercept_stderr}
r^2={linreg_side_1.rvalue ** 2}
pvalue={linreg_side_1.pvalue}
Наклон значим? {"Да" if linreg_side_1.pvalue < significance else "Нет"}

Второе зеркало:
Количество = {len(side_2_data)}
Среднее={y_side_2.mean()}
Ст. откл={y_side_2.std()}
slope={slope_side_2} 
slope_stderr={linreg_side_2.stderr}
intercept={intercept_side_2} 
intercept_stderr={linreg_side_2.intercept_stderr}
r^2={linreg_side_2.rvalue ** 2}
pvalue={linreg_side_2.pvalue}
Наклон значим? {"Да" if linreg_side_2.pvalue < significance else "Нет"}"""

                    create_and_save_figure(path,
                                           y_rows=[y_side_1, y_side_2, [line_y0_side_1, line_y1_side_1],
                                                   [line_y0_side_2, line_y1_side_2]],
                                           x_rows=[x_side_1, x_side_2, [line_x0_side_1, line_x1_side_1],
                                                   [line_x0_side_2, line_x1_side_2]],
                                           title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости",
                                           xlabel="Яркость", ylabel="Отклонение датчика",
                                           fmt_list=[".", ".", "--", "--"],
                                           legend_title="Сторона зеркала",
                                           legend=["Первая", "Вторая", "Первая", "Вторая"],
                                           text=text, xlim=xlim, ylim=ylim)
                    pbar.update(1)

    def visit_DeviationsBySurface(self, task: DatabaseTasks.DeviationsBySurface):
        data = task.get_data()
        with tqdm.tqdm(total=15 * 10, desc="Saving graphs (DeviationsBySurface)") as pbar:
            for channel in range(5, 20):
                ch_data = data[data["channel"] == channel]
                xlim = (ch_data["area_avg"].min(), ch_data["area_avg"].max())
                ylim = (ch_data["deviation"].min(), ch_data["deviation"].max())
                for sensor_i in range(10):
                    file_name = f"Датчик {sensor_i}.png"
                    path = get_graphs_path_and_create(task, file_name, inner_dir=f"Канал {channel}")

                    ch_sens_data = ch_data[ch_data["sensor"] == sensor_i]

                    filt_sea = ch_sens_data["surface_type"] == vars.SurfaceType.SEA.value
                    filt_snow = ch_sens_data["surface_type"] == vars.SurfaceType.SNOW.value
                    sea_data = ch_sens_data.loc[filt_sea]
                    snow_data = ch_sens_data.loc[filt_snow]
                    x_sea = sea_data["area_avg"].to_numpy()
                    y_sea = sea_data["deviation"].to_numpy()
                    x_snow = snow_data["area_avg"].to_numpy()
                    y_snow = snow_data["deviation"].to_numpy()

                    linreg_sea = linregress(x_sea.astype(float), y_sea.astype(float))
                    linreg_snow = linregress(x_snow.astype(float), y_snow.astype(float))
                    slope_sea, intercept_sea = linreg_sea.slope, linreg_sea.intercept
                    slope_snow, intercept_snow = linreg_snow.slope, linreg_snow.intercept
                    line_x0_sea = x_sea.min()
                    line_x1_sea = x_sea.max()
                    line_y0_sea = line_x0_sea * slope_sea + intercept_sea
                    line_y1_sea = line_x1_sea * slope_sea + intercept_sea
                    line_x0_snow = x_snow.min()
                    line_x1_snow = x_snow.max()
                    line_y0_snow = line_x0_snow * slope_snow + intercept_snow
                    line_y1_snow = line_x1_snow * slope_snow + intercept_snow

                    significance = 0.05
                    text = f"""Море:
Количество = {len(sea_data)}
Среднее={y_sea.mean()}
Ст. откл={y_sea.std()}
slope={slope_sea} 
slope_stderr={linreg_sea.stderr}
intercept={intercept_sea} 
intercept_stderr={linreg_sea.intercept_stderr}
r^2={linreg_sea.rvalue ** 2}
pvalue={linreg_sea.pvalue}
Наклон значим? {"Да" if linreg_sea.pvalue < significance else "Нет"}

Снег:
Количество = {len(snow_data)}
Среднее={y_snow.mean()}
Ст. откл={y_snow.std()}
slope={slope_snow} 
slope_stderr={linreg_snow.stderr}
intercept={intercept_snow} 
intercept_stderr={linreg_snow.intercept_stderr}
r^2={linreg_snow.rvalue ** 2}
pvalue={linreg_snow.pvalue}
Наклон значим? {"Да" if linreg_snow.pvalue < significance else "Нет"}"""

                    create_and_save_figure(path,
                                           y_rows=[y_sea, y_snow, [line_y0_sea, line_y1_sea],
                                                   [line_y0_snow, line_y1_snow]],
                                           x_rows=[x_sea, x_snow, [line_x0_sea, line_x1_sea],
                                                   [line_x0_snow, line_x1_snow]],
                                           title=f"Зависимость отклонения датчика {sensor_i} канала {channel} от яркости",
                                           xlabel="Яркость", ylabel="Отклонение датчика",
                                           fmt_list=[".", ".", "--", "--"],
                                           legend_title="Тип поверхности", legend=["Море", "Снег", "Море", "Снег"],
                                           text=text,
                                           xlim=xlim, ylim=ylim
                                           )
                    pbar.update(1)

    def visit_AreaAvgStdTask(self, task: DatabaseTasks.AreaAvgStdTask):
        data = task.get_data()
        with tqdm.tqdm(total=15, desc="Saving graphs (AreaAvgStdTask)") as pbar:
            for channel in range(5, 20):
                path = get_graphs_path_and_create(task, f"Канал {channel}")
                ch_data = data[data.channel == channel]
                plot = sns.lmplot(data=ch_data, x="area_avg", y="area_std", hue="k_mirror_side", scatter=True,
                                  scatter_kws=dict(s=2), fit_reg=False)
                plot.fig.suptitle(f"Зависимость ст. отклонения области от средней яркости (канал {channel})")
                plot.fig.savefig(path, dpi=300)
                pbar.update(1)

    def visit_NeighboringMirrorsDifference(self, task: DatabaseTasks.NeighboringMirrorsDifference):
        data = task.get_data()
        whole_area = data["whole_area"]
        each_sensor = data["each_sensor"]
        for channel in trange(5, 20, desc="Saving graphs (NeighboringMirrorsDifference, whole_area)"):
            path = get_graphs_path_and_create(task, f"Канал {channel}", inner_dir="Среднее по всей области")
            ch_data = whole_area[whole_area.CHANNEL == channel]
            g = sns.relplot(data=ch_data, x="avg_value", y="difference", kind="scatter", s=3)
            g.fig.suptitle(f"Разница между ср. яркостью областей разных зеркал\nКанал {channel}")
            plt.grid()
            plt.savefig(path, dpi=300)
            plt.close()
        with tqdm.tqdm(total=150, desc="Saving graphs (NeighboringMirrorsDifference, each_sensor)") as pbar:
            for channel in trange(5, 20):
                ch_data = each_sensor[each_sensor.CHANNEL == channel]

                # path = get_graphs_path_and_create(task, f"Канал {channel}",
                #                                   inner_dir=f"Среднее по отдельному датчику")
                # ax = sns.histplot(data=ch_data, x="difference", hue="sensor", kde=True, palette="tab10")
                # plt.savefig(path, dpi=300)
                # plt.close()

                diff_lim = [ch_data.difference.min(), ch_data.difference.max()]
                for sensor in range(10):
                    path = get_graphs_path_and_create(task, f"Датчик {sensor}",
                                                      inner_dir=f"Среднее по отдельному датчику/Канал {channel}")
                    sensor_data = ch_data[ch_data.sensor_i == sensor]
                    g = sns.relplot(data=sensor_data, x="avg_value", y="difference", kind="scatter", s=3)
                    g.fig.suptitle(
                        f"Разница между ср. яркостью датчиков разных зеркал\nКанал {channel} Датчик {sensor}")
                    avg_difference = sensor_data.difference.mean()
                    std = sensor_data.difference.std()
                    g.set(ylim=diff_lim)
                    plt.text(sensor_data.avg_value.mean(), avg_difference, f"avg={avg_difference}\nstd={std}")
                    plt.grid()
                    # ax = sns.histplot(data=sensor_data, x="difference", kde=True)
                    # ax.text(0, 0, f"avg={avg_difference}\nstd={std}")
                    # plt.xlim(*diff_lim)

                    plt.savefig(path, dpi=300)
                    plt.close()
                    pbar.update(1)

    def visit_FindSpectreBrightness(self, task: DatabaseTasks.FindSpectreBrightness):
        data = task.get_data()
        sea = data["sea"]
        snow = data["snow"]

        x = []
        y = []
        for area_id in sea.area_id.unique():
            x.append(sea[sea.area_id == area_id].CHANNEL)
            y.append(sea[sea.area_id == area_id].area_avg)
        path = get_graphs_path_and_create(task, "Спектры (на воде)")
        create_and_save_figure(path, y_rows=y, x_rows=x, grid=True, xlabel="Канал", ylabel="Ср. яркость области",
                               title="Зависимость яркости области от канала (на воде)")

        x = []
        y = []
        for area_id in snow.area_id.unique():
            x.append(snow[snow.area_id == area_id].CHANNEL)
            y.append(snow[snow.area_id == area_id].area_avg)
        path = get_graphs_path_and_create(task, "Спектры (на льду)")
        create_and_save_figure(path, y_rows=y, x_rows=x, grid=True, xlabel="Канал", ylabel="Ср. яркость области",
                               title="Зависимость яркости области от канала (на льду)")

    def visit_DeviationsByY(self, task: DatabaseTasks.DeviationsByY):
        data = task.get_data()
        for channel in range(5, 20):
            # path = get_graphs_path_and_create(task, f"Датчик {sensor}", inner_dir=f"Канал {channel}")
            path = get_graphs_path_and_create(task, f"Канал {channel}")
            ch_data = data[(data.channel == channel)]
            # sensor_data = data[(data.channel == channel) & (data.sensor == sensor)]
            # for sensor in range(10):
            #     path = get_graphs_path_and_create(task, f"Датчик {sensor}", inner_dir=f"Канал {channel}")
            #     sensor_data = data[(data.channel == channel) & (data.sensor == sensor)]
            sns.lmplot(data=ch_data, x="y", y="deviation", hue="sensor", scatter_kws=dict(s=2))
            plt.savefig(path, dpi=300)
            plt.close()
