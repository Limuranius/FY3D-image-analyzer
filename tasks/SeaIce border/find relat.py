from matplotlib import pyplot as plt

from database import ChannelArea, FY3DImageArea
import numpy as np
from scipy.optimize import minimize
import seaborn as sns
import pandas as pd


def find_relation_between_sensors(
        area: ChannelArea,
        main_sensor: int,
        sensors: list[int]) -> float:
    sea_mask_row = area.sea_mask[main_sensor]
    only_sea_main_sensor = area.to_numpy()[main_sensor][sea_mask_row]
    only_sea_sensor = np.array([
        area.to_numpy()[sensor][sea_mask_row]
        for sensor in sensors
    ])
    diff = only_sea_sensor - only_sea_main_sensor

    true_noise = only_sea_main_sensor - area.sea_value

    x0 = np.array([0] * len(sensors))
    res = minimize(
        fun=error_func,
        x0=x0,
        args=(diff, true_noise),
    )

    predicted_noise = (diff * res.x.reshape(-1, 1)).sum(axis=0)
    df = pd.DataFrame(columns=["x", "y", "type"])
    for x, y in enumerate(true_noise):
        df.loc[len(df)] = [x, y, "True noise"]
    for x, y in enumerate(predicted_noise):
        df.loc[len(df)] = [x, y, "Predicted noise"]
    sns.relplot(
        data=df,
        x="x",
        y="y",
        hue="type",
        kind="line"
    )
    plt.show()

def error_func(
        coeff: np.ndarray,
        diff: np.ndarray,
        true_noise: np.ndarray,
) -> float:
    predicted_noise = diff * coeff.reshape(-1, 1)
    error = (true_noise - predicted_noise) ** 2
    return error.sum()

find_relation_between_sensors(
    area=FY3DImageArea.get(id=8919).get_channel_area(8),
    main_sensor=0,
    sensors=[7, 8, 9]
)
