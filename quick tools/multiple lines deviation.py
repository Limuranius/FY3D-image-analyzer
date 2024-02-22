import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from database import FY3DImage
from utils import some_utils, save_data_utils
import os
from scipy.stats import linregress




if not os.path.isdir("lines"):
    os.mkdir("lines")

"""
Снимок 1  119
Снимок 2  118
Снимок 3  115
Снимок 4  113
"""

IMG_ID = 113
CHUNK_WIDTH = 5
CHANNEL = 10

"""
Графики отклонений
Графики наклонов
"""

RECTS = {
    119: [
        (280, 320, 1040),
        (350, 280, 1040),
        (610, 450, 1340)
    ],
    118: [
        (10, 300, 1180),
        (40, 300, 1040),
        (80, 300, 960)
    ],
    115: [
        (310, 610, 1490),
        (350, 680, 1320),
        (390, 760, 1480)
    ],
    113: [
        (690, 600, 1860),
        (720, 600, 1860),
        (750, 600, 1860),
    ]
}

SEA_ICE_THRESHOLDS = {
    119: {8: 1100, 10: 1100},
    118: {8: 1100, 10: 1100},
    115: {8: 400, 10: 400},
    113: {8: 400, 10: 450}
}

SEA_ICE_THRESHOLD = SEA_ICE_THRESHOLDS[IMG_ID][CHANNEL]
RECTS = RECTS[IMG_ID]

img = FY3DImage.get(id=IMG_ID)
picture = img.get_colored_picture()

sheets = []

columns = [
    "x",
    "BB_value",
    "is_water",
    "sensor",
    "avg_dn",
    "deviation",
    "dev_norm",
    "Наклон 10 датчиков",
    "r^2 1",

    "avg_dn калиброванное (+с вычетом BB)",
    "cal_deviation",
    "cal_dev_norm",
    "Наклон 10 датчиков после калибровки",
    "r^2 2",
]

for (y, x_min, x_max) in RECTS:
    width = x_max - x_min
    some_utils.draw_rectangle(picture, x_min, y, width, 10, "#FFFF00")
    data = pd.DataFrame(columns=columns,
                        index=range(10 * (width // CHUNK_WIDTH)))
    area = img.get_area(x=x_min, y=y, h=10, w=width)
    i = 0

    ch_area = area.get_vis_channel(CHANNEL)
    del area.cached_data[area.id]

    row_bb = img.get_BB_value(CHANNEL, y)
    cal_ch_area = some_utils.DN_to_Ref(ch_area - row_bb, img, CHANNEL)

    for x in range(0, x_max - x_min, CHUNK_WIDTH):
        chunk = ch_area[:, x: x + CHUNK_WIDTH]
        chunk_avg = chunk.mean()

        cal_chunk = cal_ch_area[:, x: x + CHUNK_WIDTH]
        cal_chunk_avg = cal_chunk.mean()

        is_water = chunk_avg < SEA_ICE_THRESHOLD

        sensor_df = pd.DataFrame(columns=columns, index=range(10))
        for sensor in range(10):
            sensor_avg = chunk[sensor].mean()
            deviation = sensor_avg - chunk_avg
            dev_norm = deviation / chunk_avg

            sensor_cal_avg = cal_chunk[sensor].mean()
            cal_deviation = sensor_cal_avg - cal_chunk_avg
            cal_deviation_norm = cal_deviation / cal_chunk_avg

            sensor_df.loc[sensor] = [x, row_bb, is_water, sensor, chunk_avg, deviation, dev_norm, None, None,
                                     cal_chunk_avg, cal_deviation, cal_deviation_norm, None, None]

        lin = linregress(x=sensor_df["sensor"].to_list(), y=sensor_df["dev_norm"].to_list())
        cal_lin = linregress(x=sensor_df["sensor"].to_list(), y=sensor_df["cal_dev_norm"].to_list())
        sensor_df["Наклон 10 датчиков"] = lin.slope
        sensor_df["r^2 1"] = lin.rvalue ** 2
        sensor_df["Наклон 10 датчиков после калибровки"] = cal_lin.slope
        sensor_df["r^2 2"] = cal_lin.rvalue ** 2

        for sensor in range(10):
            data.loc[i] = sensor_df.loc[sensor]
            i += 1


    sheets.append((f"{y=}", data))
    graph_data = data[data.sensor.isin([0, 9])]
    # graph_data.loc[:, "deviation"] = graph_data.deviation / graph_data.avg_dn
    # g = sns.relplot(data=graph_data, x="x", y="deviation", hue="sensor", kind="line", height=6, aspect=2,
    #                 palette="tab10")
    # g.set(ylim=(-25, 25))

    # g = sns.relplot(data=graph_data, x="x", y="slope", hue="sensor", kind="line", height=6, aspect=2,
    #                 palette="tab10")
    # g.set(ylim=(-0.05, 0.05))

    # plt.grid()
    # plt.savefig(f"lines/{y=}.jpg", dpi=300)
    # plt.close()

# results_sheet = pd.DataFrame(columns=["area", "sensor", "surface_type", "avg_slope", "std"])
# for sheet_name, slope_sheet in sheets:
#     for sensor in range(10):
#         water_data = slope_sheet[(slope_sheet.is_water == True) & (slope_sheet.sensor == sensor)]
#         snow_data = slope_sheet[(slope_sheet.is_water == False) & (slope_sheet.sensor == sensor)]
#         results_sheet.loc[len(results_sheet)] = [
#             sheet_name,
#             sensor,
#             "Вода",
#             water_data.slope.mean(),
#             water_data.slope.std(),
#         ]
#         results_sheet.loc[len(results_sheet)] = [
#             sheet_name,
#             sensor,
#             "Лёд",
#             snow_data.slope.mean(),
#             snow_data.slope.std(),
#         ]
# results_sheet = results_sheet.sort_values(['sensor', 'surface_type'])
# sheets.insert(0, ("Средние наклоны", results_sheet))

save_data_utils.save_excel_dataframe("lines/Отклонения и наклоны.xlsx", sheets, header=True)
picture.save("lines/Снимок с отмеченными областями.jpg")
