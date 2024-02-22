import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from database import FY3DImageArea
from optimize_funcs import *
import seaborn as sns
import timeresults
import utils

sns.set_style("darkgrid")


def visualize_sensor(
        sensor_coeffs: np.ndarray,
        area_id: int,
        sensor: int
):
    channel_area = FY3DImageArea.get(id=area_id).get_channel_area(8)
    arr_area = channel_area.to_numpy()
    median_values = channel_area.median_values

    true = row_true_noise(arr_area, sensor_coeffs, sensor, median_values)
    predicted = row_predicted_noise(arr_area, sensor_coeffs, sensor)

    x = list(range(len(true)))
    plt.plot(x, true)
    plt.plot(x, predicted)
    plt.show()


def visualize_all(
        coeffs: np.ndarray,
        ids: list[int],
        path: str
):
    areas = [FY3DImageArea.get(id=area_id).get_channel_area(8) for area_id in ids]

    df = pd.DataFrame(columns=["area_id", "sensor", "x", "value", "type"])

    for sensor in range(10):
        sensor_coeffs = coeffs[sensor]
        for area_id, area in zip(ids, areas):
            arr_area = area.to_numpy()
            median_values = area.median_values

            true = row_true_noise(arr_area, sensor_coeffs, sensor, median_values)
            predicted = row_predicted_noise(arr_area, sensor_coeffs, sensor)

            for x in range(len(true)):
                df.loc[len(df)] = [area_id, sensor, x, true[x], "true"]
                df.loc[len(df)] = [area_id, sensor, x, predicted[x], "predicted"]

    sns.relplot(
        data=df,
        x="x",
        y="value",
        hue="type",
        col="area_id",
        row="sensor",
        kind="line",
        facet_kws={"sharey": False, "sharex": False}
    )

    plt.savefig(path, dpi=300)
    plt.close()


def func_values(df: pd.DataFrame, path: str):
    """df: sensor | iteration | function_value"""
    sns.relplot(
        data=df,
        x="iteration",
        y="function_value",
        row="sensor",
        kind="line",
        facet_kws={"sharey": False, "sharex": False}
    )
    plt.savefig(path, dpi=300)
    plt.close()


def save_contrasted_area(
        image_channel: np.ndarray,
        path: str,
        x: int,
        y: int,
        w: int,
        h: int,
        min_value: int,
        max_value: int
) -> None:
    new_img = utils.some_utils.change_contrast(image_channel, min_value, max_value)
    new_img = new_img[y: y + h, x: x + w]
    plt.imshow(new_img, cmap="gray")
    plt.grid(False)
    plt.savefig(path, dpi=300)
    plt.close()


def visualize_sensors_relation(df: pd.DataFrame, path: str) -> None:
    """df: main_sensor | other_sensor | relation | surface_type"""
    sns.displot(
        data=df,
        x="relation",
        row="main_sensor",
        col="other_sensor",
        hue="surface_type"
    )
    plt.savefig(path, dpi=300)
    plt.close()


def visualize_coeffs(coeffs: np.ndarray, path: str) -> None:
    if len(coeffs.shape) == 1:
        df = pd.DataFrame(columns=["sensor", "coeff_value"])
        for sensor in range(10):
            coeff_value = coeffs[sensor]
            df.loc[len(df)] = [sensor, coeff_value]
        sns.relplot(
            data=df,
            x="sensor",
            y="coeff_value",
            kind="line"
        )
    elif len(coeffs.shape) == 2:
        df = pd.DataFrame(columns=["main_sensor", "sensor", "coeff_value"])
        for main_sensor in range(10):
            for sensor in range(10):
                coeff_value = coeffs[main_sensor, sensor]
                df.loc[len(df)] = [main_sensor, sensor, coeff_value]
        sns.relplot(
            data=df,
            x="sensor",
            y="coeff_value",
            row="main_sensor",
            kind="line"
        )
    else:
        raise Exception("???")
    plt.savefig(path, dpi=300)
    plt.close()

