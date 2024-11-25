import numpy as np

MAX_NOISE = 300
# MAX_NOISE = 10 ** 9


"""
Порядок входных параметров функций ошибок:
    coeffs - оптимизируемые параметры
    area, 
    target_values
    [sensor]
    [static_coeffs]
"""


def total_error_only_b(
        b_coeffs: np.ndarray,  # <-- optimizing these coefficients
        area: np.ndarray,
        target_values: np.ndarray,
        flat_a_coeffs_static: np.ndarray,
) -> float:
    """
    b_coeffs: shape(1, 20)
    flat_a_coeffs_static: shape(1, 100)
    """
    coeffs = np.array([*flat_a_coeffs_static, *b_coeffs])
    return total_error(coeffs, area, target_values)


def total_error(
        coeffs: np.ndarray,  # <-- optimizing these coefficients
        area: np.ndarray,
        target_values: np.ndarray,
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
            target_values,
            sensor,
        )
        error += sensor_error
    return error


def total_sensor_error_b_only(
        b_coeffs: np.ndarray,  # <-- optimizing these coefficients
        area: np.ndarray,
        target_values: np.ndarray,
        sensor: int,
        sensor_a_coeffs: np.ndarray,
) -> float:
    """
    sensor_a_coeffs: shape(1, 10)
    b_coeffs: shape(1, 20)
    """
    sensor_coeffs = np.array([*sensor_a_coeffs, *b_coeffs])
    return total_sensor_error(sensor_coeffs, area, target_values, sensor)


def total_sensor_error_a_only(
        sensor_a_coeffs: np.ndarray,  # <-- optimizing these coefficients
        area: np.ndarray,
        target_values: np.ndarray,
        sensor: int,
        b_coeffs: np.ndarray,
) -> float:
    """
    sensor_a_coeffs: shape(1, 10)
    b_coeffs: shape(1, 20)
    """
    sensor_coeffs = np.array([*sensor_a_coeffs, *b_coeffs])
    return total_sensor_error(sensor_coeffs, area, target_values, sensor)


def total_sensor_error(
        sensor_coeffs: np.ndarray,  # <-- optimizing these coefficients
        area: np.ndarray,
        target_values: np.ndarray,
        sensor: int,
) -> float:
    """
    Суммарная ошибка на сенсоре sensor у области area при текущих коэффициентах sensor_coeffs
    sensor_coeffs: shape(1, 30)
    """
    predicted = row_predicted_noise(area, sensor_coeffs, sensor)
    error = target_values - predicted

    error[np.abs(target_values) > MAX_NOISE] = 0

    error_sq = error ** 2
    return error_sq.sum()


def row_regress_values(
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
    i_values = row_regress_values(area, coeffs, sensor)
    for j in range(10):
        j_values = row_regress_values(area, coeffs, j)
        diff = i_values - j_values
        col_diff[j] = diff

    a_coeffs = coeffs[0:10]
    a_coeffs = a_coeffs.reshape((10, 1))

    # deviations = i_values - area[sensor]
    # noise = col_diff * a_coeffs + deviations

    noise = col_diff * a_coeffs

    return noise.sum(axis=0)
