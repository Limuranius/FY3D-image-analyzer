import h5py
import pandas as pd
from utils import some_utils, save_data_utils
import os
from scipy.stats import linregress

if not os.path.isdir("lines"):
    os.mkdir("lines")

CHUNK_WIDTH = 5
CHANNEL = 8

RECTS = [
    (280, 320, 1040),
    (350, 280, 1040),
    (610, 450, 1340)
]

file = h5py.File(r"D:\Снимки со спутников\10.11.23 калибровка\calibrated.hdf", "r")
EV_1KM_RefSB = file["EV_1KM_RefSB"]

sheets = []

columns = [
    "x",
    "sensor",
    "avg_dn",
    "deviation",
    "dev_norm",
    "Наклон 10 датчиков",
]


for (y, x_min, x_max) in RECTS:
    width = x_max - x_min
    data = pd.DataFrame(columns=columns,
                        index=range(10 * (width // CHUNK_WIDTH)))
    area = EV_1KM_RefSB[:, y: y + 10, x_min: x_min + width]
    i = 0

    ch_area = area[CHANNEL - 5]

    for x in range(0, x_max - x_min, CHUNK_WIDTH):
        chunk = ch_area[:, x: x + CHUNK_WIDTH]
        chunk_avg = chunk.mean()

        sensor_df = pd.DataFrame(columns=columns, index=range(10))
        for sensor in range(10):
            sensor_avg = chunk[sensor].mean()
            deviation = sensor_avg - chunk_avg
            dev_norm = deviation / chunk_avg
            sensor_df.loc[sensor] = [x, sensor, chunk_avg, deviation, dev_norm, None]

        lin = linregress(x=sensor_df["sensor"].to_list(), y=sensor_df["dev_norm"].to_list())
        sensor_df["Наклон 10 датчиков"] = lin.slope

        for sensor in range(10):
            data.loc[i] = sensor_df.loc[sensor]
            i += 1

    sheets.append((f"{y=}", data))
    graph_data = data[data.sensor.isin([0, 9])]

save_data_utils.save_excel_dataframe("lines/Отклонения и наклоны (calibrated).xlsx", sheets, header=True)
