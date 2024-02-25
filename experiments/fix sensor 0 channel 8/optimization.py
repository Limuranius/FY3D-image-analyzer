from database import FY3DImageArea, FY3DImage
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
from utils.some_utils import change_contrast
import seaborn as sns
import numpy as np
from scipy.optimize import minimize


MAX_NOISE = 100

CONCRETE_SENSORS = {
    0: [1, 2, 3],
    1: [0],
    2: [1, 3, 4],
    3: [2, 4, 5],
    4: [3, 5, 6],
    5: [4, 6, 7],
    6: [5, 7, 8, 9],
    7: [6, 8, 9],
    8: [5, 6, 7, 9],
    9: [6, 7, 8],
}



def get_median_image(image):
    return median_filter(image, size=5)


def get_area(area_id: int, image):
    area = FY3DImageArea.get(id=area_id)
    x, y, w, h = area.x, area.y, area.width, area.height
    channel_area = area.get_channel_area(8)
    area_numpy = channel_area.to_numpy()
    median_values = get_median_image(image)[y: y + h, x: x + w]
    return area_numpy, median_values


def optimize(
        area,
        median_values,
        sensor
):
    true_values = area[sensor] - median_values[sensor]
    # coeffs = np.zeros(10)

    depend_sensors = CONCRETE_SENSORS[sensor]
    coeffs = np.zeros(len(depend_sensors))

    res = minimize(
        fun=error_sum,
        x0=coeffs,
        args=(area, true_values, sensor)
    )
    return res.x

    # coeffs = np.zeros(10)
    # for i, sensor_i in enumerate(CONCRETE_SENSORS[sensor]):
    #     coeffs[sensor_i] = res.x[i]
    # return coeffs


def error_sum(
        coeffs,
        area,
        true_values,
        sensor
):
    predicted_values = get_predicted_values(coeffs, area, sensor)
    error = true_values - predicted_values
    error[np.abs(true_values) > MAX_NOISE] = 0
    error_sq = error ** 2
    return error_sq.sum()


def get_predicted_values(
        coeffs,
        area,
        sensor
):
    depend_sensors = CONCRETE_SENSORS[sensor]
    sensor_row = area[sensor]
    depend_area = area[depend_sensors]
    sens_diff = depend_area - sensor_row
    sens_diff_coeff = sens_diff * coeffs.reshape(len(depend_sensors), 1)
    predicted_values = sens_diff_coeff.sum(axis=0)

    # sens_diff = area - area[sensor]
    # sens_diff_coeff = sens_diff * coeffs.reshape(10, 1)
    # predicted_values = sens_diff_coeff.sum(axis=0)
    return predicted_values


def connect_areas(area_ids: list[int], image) -> tuple[np.ndarray, np.ndarray]:
    # Connecting areas side by side
    areas = []
    medians = []
    for area_id in area_ids:
        area, median_values = get_area(area_id, image)
        areas.append(area)
        medians.append(median_values)
    arr_area = np.concatenate(areas, axis=1)
    median_values = np.concatenate(medians, axis=1)
    return arr_area, median_values
