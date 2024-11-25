import pandas as pd

import optimize_funcs
from scipy.optimize import minimize
from tqdm import trange
import numpy as np
from database import ChannelArea, FY3DImageArea
import utils

MEDIAN_SIZE = 5


def prepare_area(
        channel_area: ChannelArea
) -> tuple[np.ndarray, np.ndarray]:
    """Returns area and target values"""

    area = channel_area.to_numpy()

    median_values = utils.area_utils.area_to_surrounding_median(channel_area, size=5)
    # median_values = utils.area_utils.area_to_surrounding_median(channel_area, size=(1, 20))
    # median_values = utils.area_utils.two_peak_filter(area)

    bb = channel_area.get_black_body_value()
    area -= int(bb)
    median_values -= int(bb)

    target_values = area - median_values

    return area, target_values


def __iterative_optimize(
        coeffs: np.ndarray,
        n_iters: int,
        error_function,
        args,
) -> tuple[np.ndarray, list[int]]:
    """returns coeffs, list of function results"""
    methods = ["BFGS", "nelder-mead", "Powell", "CG"]
    results = []
    for i in trange(n_iters):
        method = methods[i % len(methods)]
        res = minimize(
            fun=error_function,
            x0=coeffs,
            args=args,
            method=method
        )
        results.append(res.fun)
        coeffs = res.x
    return coeffs, results


def __connect_areas(area_ids: list[int], channel: int) -> tuple[np.ndarray, np.ndarray]:
    # Connecting areas side by side
    areas = []
    target_values = []
    for area_id in area_ids:
        area = FY3DImageArea.get(id=area_id)
        channel_area = area.get_channel_area(channel)

        area_np, target_np = prepare_area(channel_area)

        areas.append(area_np)
        target_values.append(target_np)

    arr_area = np.concatenate(areas, axis=1)
    arr_target = np.concatenate(target_values, axis=1)
    return arr_area, arr_target


def iterate_sensors(
        area_ids: list[int],
        n_iters: int,
        start_coeffs: np.ndarray,
        sensor_error_function,
        channel: int,
        static_coeffs=None
):
    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])
    coeffs = []
    area, target_values = __connect_areas(area_ids=area_ids, channel=channel)

    for sensor in range(10):
        sensor_target_values = target_values[sensor]
        if static_coeffs is not None:
            args = (area, sensor_target_values, sensor, static_coeffs)
        else:
            args = (area, sensor_target_values, sensor)
        sensor_coeffs = start_coeffs[sensor]
        sensor_coeffs, fun_values = __iterative_optimize(
            coeffs=sensor_coeffs,
            n_iters=n_iters,
            error_function=sensor_error_function,
            args=args
        )
        coeffs.append(sensor_coeffs)
        for iteration, fun in enumerate(fun_values):
            fun_df.loc[len(fun_df)] = [sensor, iteration, fun]
    coeffs = np.array(coeffs)
    return coeffs, fun_df


def optimize_all_sensors(
        area_ids: list[int],
        n_iters: int,
        start_coeffs: np.ndarray,
        channel: int
) -> tuple[np.ndarray, pd.DataFrame]:
    """returns 10x30 array of coeffs and 10 x n_iters dataframe of minimized function values"""
    return iterate_sensors(
        area_ids=area_ids,
        n_iters=n_iters,
        start_coeffs=start_coeffs,
        sensor_error_function=optimize_funcs.total_sensor_error,
        channel=channel,
    )


def optimize_all_sensors_only_b(
        area_ids: list[int],
        n_iters: int,
        a_coeffs: np.ndarray,
        channel: int,
) -> tuple[np.ndarray, pd.DataFrame]:
    """returns 10x30 array of coeffs and 10 x n_iters dataframe of minimized function values"""
    area, target_values = __connect_areas(area_ids=area_ids, channel=channel)

    b_coeffs = np.zeros((10, 20))
    b_coeffs[:, 0:10] = 1
    a_coeffs_flat = a_coeffs.flatten()

    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])

    b_coeffs, fun_values = __iterative_optimize(
        coeffs=b_coeffs,
        n_iters=n_iters,
        error_function=optimize_funcs.total_error_only_b,
        args=(area, target_values, a_coeffs_flat)
    )

    for iteration, value in enumerate(fun_values):
        fun_df.loc[len(fun_df)] = ["all", iteration, value]

    coeffs = np.empty((10, 30))
    coeffs[:, 0:10] = a_coeffs
    coeffs[:, 10:30] = b_coeffs
    return coeffs, fun_df


def optimize_at_once(
        area_ids: int | list[int],
        n_iters: int,
        flat_coeffs: np.ndarray,
        channel: int,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Takes 1x120 coeffs"""
    area, target_values = __connect_areas(area_ids=area_ids, channel=channel)

    fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])

    flat_coeffs, fun_values = __iterative_optimize(
        coeffs=flat_coeffs,
        n_iters=n_iters,
        error_function=optimize_funcs.total_error,
        args=(area, target_values)
    )

    for iteration, value in enumerate(fun_values):
        fun_df.loc[len(fun_df)] = ["all", iteration, value]

    coeffs = np.empty((10, 30))
    coeffs[:, 0:10] = flat_coeffs[0:100].reshape(10, 10)
    coeffs[:, 10:30] = flat_coeffs[100:120]
    return coeffs, fun_df


def bruteforce_b(
        areas: int | list[int],
        coeffs: np.ndarray,
) -> tuple[np.ndarray, pd.DataFrame]:
    # area, median_values = __connect_areas(areas)
    #
    # slope_range = np.linspace(
    #     start=1 + -20 / 4096,
    #     stop=1 + 20 / 4096,
    #     num=10
    # )
    # intercept_range = np.linspace(
    #     start=-5,
    #     stop=5,
    #     num=11
    # )
    # fun_df = pd.DataFrame(columns=["sensor", "iteration", "function_value"])
    # for sensor in range(10):
    #     min_error = float("inf")
    #     iteration = 0
    #     for slope in slope_range:
    #         for intercept in intercept_range:
    #             coeffs_copy = coeffs.copy()
    #             coeffs_copy[:, 10 + sensor] = slope
    #             coeffs_copy[:, 20 + sensor] = intercept
    #             error = total_sensor_error(
    #                 sensor_coeffs=coeffs_copy[sensor],
    #                 area=area,
    #                 sensor=sensor,
    #                 target_values=median_values
    #             )
    #             if error < min_error:
    #                 coeffs = coeffs_copy
    #             fun_df.loc[len(fun_df)] = [sensor, iteration, error]
    #             iteration += 1
    #
    # return coeffs, fun_df
    raise Exception()


def optimize_only_a(
        area_ids: list[int],
        n_iters: int,
        a_coeffs: np.ndarray,
        b_coeffs: np.ndarray,
        channel: int,
) -> tuple[np.ndarray, pd.DataFrame]:
    a_coeffs, fun_df = iterate_sensors(
        area_ids=area_ids,
        n_iters=n_iters,
        start_coeffs=a_coeffs,
        sensor_error_function=optimize_funcs.total_sensor_error_a_only,
        static_coeffs=b_coeffs,
        channel=channel,
    )
    coeffs = np.empty((10, 30))
    coeffs[:, 0:10] = a_coeffs
    coeffs[:, 10:30] = b_coeffs
    return coeffs, fun_df
