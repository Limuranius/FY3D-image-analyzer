import os.path
import pandas as pd
from scipy.optimize import minimize
import numpy as np
from database import ChannelArea, FY3DImageArea
import vars
import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

np.set_printoptions(suppress=True)

"""
coeffs:
0-9 - a
10-19 - b1
20-29 - b2
"""

OPTIMIZE_B = False
A_COEFFS = None

def optimize_b(area: np.ndarray, sensor: int, x0, a_coeffs):
    global OPTIMIZE_B, A_COEFFS
    OPTIMIZE_B = True
    A_COEFFS = a_coeffs
    return minimize(
        fun=total_error,
        x0=x0,
        args=(area, sensor)
    )


def optimize(area: np.ndarray, sensor: int, x0=None):
    if x0 is None:
        x0 = np.zeros(30)
    return minimize(
        fun=total_error,
        x0=x0,
        args=(area, sensor)
    )


def total_error(
        coeffs: np.ndarray,
        area: np.ndarray,
        sensor: int
) -> float:
    if OPTIMIZE_B:
        coeffs = np.array([*A_COEFFS, *coeffs])
    true = row_true_noise(area, coeffs, sensor)
    predicted = row_predicted_noise(area, coeffs, sensor)
    error = true - predicted
    error_sq = error ** 2
    return error_sq.sum()


def pixel_true_value(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
        col: int
) -> float:
    b1 = coeffs[10 + sensor]
    b2 = coeffs[20 + sensor]
    value = area[sensor, col]
    true_value = b1 * value + b2
    return true_value


def pixel_true_noise(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
        col: int
) -> float:
    value = area[sensor, col]
    true_value = pixel_true_value(area, coeffs, sensor, col)
    noise = value - true_value
    return noise


def pixel_predicted_noise(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
        col: int
) -> float:
    col_diff = []
    i_value = pixel_true_value(area, coeffs, sensor, col)
    for j in range(10):
        j_value = pixel_true_value(area, coeffs, j, col)
        diff = i_value - j_value
        col_diff.append(diff)
    col_diff = np.array(col_diff)

    col_values = area[:, col]
    a_coeffs = coeffs[0:10]
    noise = col_diff * a_coeffs
    return noise.sum()


def row_true_values(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
) -> np.ndarray:
    b1 = coeffs[10 + sensor]
    b2 = coeffs[20 + sensor]
    values = area[sensor]
    true_values = b1 * values + b2
    return true_values


def row_true_noise(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
) -> np.ndarray:
    values = area[sensor]
    true_values = row_true_values(area, coeffs, sensor)
    noise = values - true_values
    return noise


def row_predicted_noise(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
) -> np.ndarray:
    col_diff = np.empty_like(area)
    i_values = row_true_values(area, coeffs, sensor)
    for j in range(10):
        j_values = row_true_values(area, coeffs, j)
        diff = i_values - j_values
        col_diff[j] = diff

    a_coeffs = coeffs[0:10]
    a_coeffs = a_coeffs.reshape((10, 1))
    noise = col_diff * a_coeffs
    return noise.sum(axis=0)


def main():
    import pickle
    with open(r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\Результаты\common_coeffs.pkl", "rb") as f:
        data = pickle.load(f)
    sensor = 0
    b1 = [1] * 10
    b2 = [0] * 10
    a = data[sensor]
    area = FY3DImageArea.get(id=8917).get_channel_area(8).to_numpy()

    # x0 = np.array([*a, *b1, *b2])
    # res = optimize(area, sensor, x0=x0)
    # coeffs = res.x

    x0 = np.array([*b1, *b2])
    res = optimize_b(area, sensor, x0=x0, a_coeffs=a)
    coeffs = np.array([*a, *res.x])
    print(res.x)

    true = row_true_noise(area, coeffs, sensor)
    predicted = row_predicted_noise(area, coeffs, sensor)

    x = list(range(len(true)))
    plt.plot(x, true)
    plt.plot(x, predicted)
    plt.show()

main()