from database import FY3DImageArea, FY3DImage
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
from utils.some_utils import change_contrast
import seaborn as sns
import numpy as np
from scipy.optimize import minimize


MAX_NOISE = 100


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
        sensor,
        n_iters
):
    true_values = area[sensor] - median_values[sensor]
    coeffs = np.zeros(10)

    methods = ["BFGS", "Nelder-Mead", "Powell", "CG", "COBYLA"]
    for _ in range(n_iters):
        method = methods[_ % len(methods)]
        res = minimize(
            fun=error_sum,
            x0=coeffs,
            args=(area, true_values, sensor),
            method=method
        )
        print(res.fun)
        coeffs = res.x
    return coeffs

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
    sens_diff = area - area[sensor]
    sens_diff_coeff = sens_diff * coeffs.reshape(10, 1)
    predicted_values = sens_diff_coeff.sum(axis=0)
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
