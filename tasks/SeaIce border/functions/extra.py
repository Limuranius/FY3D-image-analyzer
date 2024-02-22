import pandas as pd

from optimize_funcs import *
from scipy.optimize import minimize
from tqdm import trange
import numpy as np
from database import ChannelArea, FY3DImageArea


def __optimize(
        area: np.ndarray,
        sensor: int,
        median_values,
        x0,
        method: str = "BFGS"
):
    return minimize(
        fun=total_sensor_error,
        x0=x0,
        args=(area, sensor, median_values),
        method=method
    )


def __iterative_optimize(
        area: np.ndarray,
        x0: np.ndarray,
        median_values: np.ndarray,
        n_iters: int,
        sensor: int
) -> tuple[np.ndarray, list[int]]:
    """returns coeffs, list of function results"""
    methods = ["BFGS", "nelder-mead", "CG"]
    results = []
    for i in trange(n_iters):
        method = methods[i % len(methods)]
        res = __optimize(area, sensor, median_values, x0=x0, method=method)
        results.append(res.fun)
        x0 = res.x
    return x0, results


def __optimize_one(
        area_id: int,
        sensor: int,
        n_iters: int,
        x0: np.ndarray,
):
    channel_area = FY3DImageArea.get(id=area_id).get_channel_area(8)
    arr_area = channel_area.to_numpy()
    median_values = channel_area.median_values

    return __iterative_optimize(arr_area, x0, median_values, n_iters, sensor)


def __connect_areas(area_ids: list[int]) -> tuple[np.ndarray, np.ndarray]:
    # Connecting areas side by side
    areas = []
    medians = []
    for area_id in area_ids:
        channel_area = FY3DImageArea.get(id=area_id).get_channel_area(8)
        areas.append(channel_area.to_numpy())
        medians.append(channel_area.median_values)
    arr_area = np.concatenate(areas, axis=1)
    median_values = np.concatenate(medians, axis=1)
    return arr_area, median_values


def __optimize_batch(
        area_ids: list[int],
        sensor: int,
        n_iters: int,
        x0: np.ndarray,
):
    arr_area, median_values = __connect_areas(area_ids)
    return __iterative_optimize(arr_area, x0, median_values, n_iters, sensor)


def optimize_dispatch(
        areas: int | list[int],
        sensor: int,
        n_iters: int,
        x0: np.ndarray,
):
    if isinstance(areas, int):
        return __optimize_one(areas, sensor, n_iters, x0)
    else:
        return __optimize_batch(areas, sensor, n_iters, x0)


def optimize_all_sensors(
        areas: int | list[int],
        n_iters: int,
        x0_arr: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    """returns 10x30 array of coeffs and 10 x n_iters dataframe of minimized function values"""
    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])

    coeffs = []
    for sensor in range(10):
        x0 = x0_arr[sensor]
        sensor_coeffs, fun_values = optimize_dispatch(areas, sensor, n_iters, x0)
        coeffs.append(sensor_coeffs)
        for iteration, fun in enumerate(fun_values):
            fun_df.loc[len(fun_df)] = [sensor, iteration, fun]

    coeffs = np.array(coeffs)
    return coeffs, fun_df


def optimize_all_sensors_only_b(
        areas: int | list[int],
        n_iters: int,
        a_coeffs: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    """returns 10x30 array of coeffs and 10 x n_iters dataframe of minimized function values"""
    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])
    area, median_values = __connect_areas(areas)
    b_coeffs = np.array([1] * 10 + [0] * 10)
    a_coeffs_flat = a_coeffs.flatten()
    methods = ["BFGS", "nelder-mead", "CG"]
    for iteration in trange(n_iters):
        method = methods[iteration % len(methods)]
        res = minimize(
            fun=total_error_only_b,
            x0=b_coeffs,
            args=(a_coeffs_flat, area, median_values),
            method=method
        )
        fun_df.loc[len(fun_df)] = ["all", iteration, res.fun]
        b_coeffs = res.x

    coeffs = np.empty((10, 30))
    coeffs[:, 0:10] = a_coeffs
    coeffs[:, 10:30] = b_coeffs
    return coeffs, fun_df


def optimize_at_once(
        areas: int | list[int],
        n_iters: int,
        flat_coeffs: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Takes 1x120 coeffs"""
    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])

    area, median_values = __connect_areas(areas)

    methods = ["BFGS", "nelder-mead", "CG"]
    for iteration in trange(n_iters):
        method = methods[iteration % len(methods)]
        res = minimize(
            fun=total_error,
            x0=flat_coeffs,
            args=(area, median_values),
            method=method
        )
        fun_df.loc[len(fun_df)] = ["all", iteration, res.fun]
        flat_coeffs = res.x

    square_coeffs = np.empty((10, 30))
    b1 = flat_coeffs[100:110]
    b2 = flat_coeffs[110:120]
    for sensor in range(10):
        sensor_a = flat_coeffs[sensor * 10: (sensor + 1) * 10]
        square_coeffs[sensor, 0:10] = sensor_a
    square_coeffs[:, 10:20] = b1
    square_coeffs[:, 20:30] = b2

    return square_coeffs, fun_df


def bruteforce_b(
        areas: int | list[int],
        coeffs: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    area, median_values = __connect_areas(areas)

    slope_range = np.linspace(
        start=1 + -20 / 4096,
        stop=1 + 20 / 4096,
        num=10
    )
    intercept_range = np.linspace(
        start=-5,
        stop=5,
        num=11
    )
    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])
    for sensor in range(10):
        min_error = float("inf")
        iteration = 0
        for slope in slope_range:
            for intercept in intercept_range:
                coeffs_copy = coeffs.copy()
                coeffs_copy[:, 10 + sensor] = slope
                coeffs_copy[:, 20 + sensor] = intercept
                error = total_sensor_error(
                    sensor_coeffs=coeffs_copy[sensor],
                    area=area,
                    sensor=sensor,
                    median_values=median_values
                )
                if error < min_error:
                    coeffs = coeffs_copy
                fun_df.loc[len(fun_df)] = [sensor, iteration, error]
                iteration += 1

    return coeffs, fun_df


def optimize_only_a(
        areas: int | list[int],
        n_iters: int,
        a_coeffs: np.ndarray,
        b_coeffs: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])
    area, median_values = __connect_areas(areas)
    methods = ["BFGS", "nelder-mead", "CG"]

    coeffs = []
    for sensor in range(10):
        sensor_a_coeffs = a_coeffs[sensor]
        for iteration in trange(n_iters):
            method = methods[iteration % len(methods)]
            res = minimize(
                fun=total_sensor_error_a_only,
                x0=sensor_a_coeffs,
                args=(b_coeffs, area, sensor, median_values),
                method=method
            )
            sensor_a_coeffs = res.x
            fun_df.loc[len(fun_df)] = [sensor, iteration, res.fun]
        coeffs.append(sensor_a_coeffs)

    a_coeffs = np.array(coeffs)
    coeffs = np.empty((10, 30))
    coeffs[:, 0:10] = a_coeffs
    coeffs[:, 10:30] = b_coeffs
    return coeffs, fun_df
