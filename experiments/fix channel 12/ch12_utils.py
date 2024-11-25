import numpy as np


def avg_filter(area: np.ndarray, window_size: int):
    result = np.empty_like(area)
    for i, row in enumerate(area):
        for j in range(len(row)):
            result[i, j] = row[j: j + window_size + 1].mean()
    return result


def predict_noise(row: np.ndarray, coeff: float, win_size: int) -> np.ndarray:
    # win_size = 20
    avg = avg_filter([row], win_size)
    delta = avg - row

    damn = np.array([row, avg[0], delta[0]])
    # noise = delta * coeff
    # noise[noise < 0] = 0

    delta = delta.astype(float)
    delta[delta < 0] = 0
    noise = (1 + coeff) ** delta - 1
    # noise = (delta) ** coeff / 100000
    # print(noise)

    return noise[0]


def get_true_sea_values(area: np.ndarray):
    sea_value = int(area[:, 0].mean())
    true_values = area.copy()
    true_values[true_values < 800] = sea_value
    return true_values
