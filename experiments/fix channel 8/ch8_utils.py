import numpy as np


def get_sensor_diff(area: np.ndarray, sensor: int):
    return area - area[sensor]


def get_true_sea_values(area: np.ndarray):
    sea_value = int(area[:, 0].mean())
    true_values = area.copy()
    true_values[true_values < 1500] = sea_value
    return true_values


def predict_noise(difference: np.ndarray, coeffs: np.ndarray):
    noise = difference * coeffs.reshape((10, 1))
    noise = noise.sum(axis=0)
    return noise


def filter_area(area: np.ndarray, coeffs: np.ndarray):
    SENSOR = 0
    height = area.shape[0]
    new_area = area.copy()
    for y in range(0, height, 10):
        rows = area[y: y + 10, :]
        diff = get_sensor_diff(rows, SENSOR)
        row_noise = predict_noise(diff, coeffs)
        new_area[y] -= row_noise.astype(int)
    return new_area
