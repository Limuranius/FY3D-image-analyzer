import numpy as np

# OPTIMIZE_B_ONLY = False
# A_COEFFS = None
MAX_NOISE = 300


# MAX_NOISE = 10 ** 9


# def set_optimize_b(status: bool, a_coeffs: np.ndarray = None):
#     global OPTIMIZE_B_ONLY, A_COEFFS
#     OPTIMIZE_B_ONLY = status
#     A_COEFFS = a_coeffs


def total_error_only_b(
        b_coeffs: np.ndarray,
        flat_a_coeffs_static: np.ndarray,
        area: np.ndarray,
        median_values: np.ndarray,
) -> float:
    coeffs = np.array([flat_a_coeffs_static, b_coeffs])
    return total_error(coeffs, area, median_values)


def total_error(
        coeffs: np.ndarray,
        area: np.ndarray,
        median_values: np.ndarray,
) -> float:
    """
    Находит ошибку по всем датчикам одновременно
    coeffs: shape(1, 120)
        0-100: a
        100-110: b1
        110-120: b2
    """
    error = 0
    for sensor in range(10):
        a = coeffs[sensor * 10: (sensor + 1) * 10]
        b1 = coeffs[100:110]
        b2 = coeffs[110:120]
        sensor_coeffs = np.array([*a, *b1, *b2])
        sensor_error = total_sensor_error(
            sensor_coeffs,
            area,
            sensor,
            median_values
        )
        error += sensor_error
    return error


def total_sensor_error_b_only(
        b_coeffs: np.ndarray,
        sensor_a_coeffs: np.ndarray,
        area: np.ndarray,
        sensor: int,
        median_values: np.ndarray,
) -> float:
    sensor_coeffs = np.array([sensor_a_coeffs, b_coeffs])
    return total_sensor_error(sensor_coeffs, area, sensor, median_values)


def total_sensor_error_a_only(
        sensor_a_coeffs: np.ndarray,
        b_coeffs: np.ndarray,
        area: np.ndarray,
        sensor: int,
        median_values: np.ndarray,
) -> float:
    sensor_coeffs = np.array([sensor_a_coeffs, b_coeffs])
    return total_sensor_error(sensor_coeffs, area, sensor, median_values)


def total_sensor_error(
        sensor_coeffs: np.ndarray,
        area: np.ndarray,
        sensor: int,
        median_values: np.ndarray,
) -> float:
    """
    Суммарная ошибка на сенсоре sensor у области area при текущих коэффициентах sensor_coeffs
    sensor_coeffs: shape(1, 30)
    """
    true = row_true_noise(area, sensor_coeffs, sensor, median_values)
    predicted = row_predicted_noise(area, sensor_coeffs, sensor)
    error = true - predicted

    error[np.abs(true) > MAX_NOISE] = 0

    error_sq = error ** 2
    return error_sq.sum()


def row_true_values(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
) -> np.ndarray:
    """
    Возвращает значения строки sensor области area по следующей формуле:
    area[sensor] * b1 + b2
    """
    b1 = coeffs[10 + sensor]
    b2 = coeffs[20 + sensor]
    values = area[sensor]
    true_values = b1 * values + b2
    return true_values


def row_true_noise(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
        median_values: np.ndarray,
) -> np.ndarray:
    """
    Возвращает истинный шум в строке sensor
    по медианным значениям области
    """
    # true_values = row_true_values(area, coeffs, sensor)
    # median_row = median_values[sensor]
    # noise = true_values - median_row
    # return noise

    median_row = median_values[sensor]
    noise = area[sensor] - median_row
    return noise


def row_predicted_noise(
        area: np.ndarray,
        coeffs: np.ndarray,
        sensor: int,
) -> np.ndarray:
    """
    Вычисляет предсказанный шум влияния соседних датчиков,
    используя коэффициенты a из coeffs
    """
    col_diff = np.empty_like(area)
    i_values = row_true_values(area, coeffs, sensor)
    for j in range(10):
        j_values = row_true_values(area, coeffs, j)
        diff = i_values - j_values
        col_diff[j] = diff

    deviations = i_values - area[sensor]
    a_coeffs = coeffs[0:10]
    a_coeffs = a_coeffs.reshape((10, 1))
    noise = col_diff * a_coeffs + deviations
    return noise.sum(axis=0)
