import os.path

import pandas as pd
from scipy.optimize import minimize
import numpy as np
from database import ChannelArea
import vars
import tqdm


NOISE_IGNORE_THRESHOLD = 300
CONCRETE_SENSORS = {sensor: list(range(10)) for sensor in range(10)}
# CONCRETE_SENSORS = {
#     0: [1, 2, 3],
#     1: [0],
#     2: [1, 3, 4],
#     3: [2, 4, 5],
#     4: [3, 5, 6],
#     5: [4, 6, 7],
#     6: [5, 7, 8, 9],
#     7: [6, 8, 9],
#     8: [5, 6, 7, 9],
#     9: [6, 7, 8],
# }


class SeaIceOptimizer:
    __process_areas: list[ChannelArea]

    def __init__(self):
        self.__process_areas = []

    def __true_noise(self, pixel_i: int, pixel_j: int, area_i: int) -> float:
        area = self.__process_areas[area_i]
        return area.true_noise[pixel_i, pixel_j]

    def __predicted_column_noise(
            self,
            phis: np.ndarray,
            area_i: int,
            col_j: int,
            sensor_i: int
    ) -> float:
        area = self.__process_areas[area_i]
        col_values = area.to_numpy()[:, col_j]
        sensor_value = col_values[sensor_i]
        diff = sensor_value - col_values
        # noises = diff * phis
        noise_sum = 0
        for sensor_j, phi_j in zip(CONCRETE_SENSORS[sensor_i], phis):
            noise_sum += diff[sensor_j] * phi_j
        # return noise.sum()
        return noise_sum

    def __total_error(self, phis: np.ndarray, sensor_i: int) -> float:
        error_sum = 0
        for area_i, area in enumerate(self.__process_areas):
            for j in range(area.w):
                true_noise = self.__true_noise(sensor_i, j, area_i)
                predicted_col_noise = self.__predicted_column_noise(phis, area_i, j, sensor_i)

                if abs(true_noise) < NOISE_IGNORE_THRESHOLD:  # TODO
                    error_sum += (true_noise - predicted_col_noise) ** 2
        return error_sum

    def __partial_derivative(self, phis: np.ndarray, phi_j: int, sensor_i: int):
        s = 0
        for area_i, area in enumerate(self.__process_areas):
            for j in range(area.w):
                true_noise = self.__true_noise(sensor_i, j, area_i)
                predicted_col_noise = self.__predicted_column_noise(phis, area_i, j, sensor_i)
                col = area.to_numpy()[:, j]

                if abs(true_noise) < NOISE_IGNORE_THRESHOLD:  # TODO
                    s += 2 * (true_noise - predicted_col_noise) * (col[phi_j] - col[sensor_i])
        return s

    def __phi_epsilon_sum_der(self, phis: np.ndarray, sensor_i: int):
        # Derivative of optimization function
        jac = []
        for sensor_j in CONCRETE_SENSORS[sensor_i]:
            jac.append(self.__partial_derivative(phis, sensor_j, sensor_i))
        return jac



    def __optimize(self) -> np.ndarray:
        result_phis = np.zeros(shape=(10, 10), dtype=np.float_)
        for sensor in tqdm.trange(10):
            depend_sensors = CONCRETE_SENSORS[sensor]
            x0 = (np.random.random(size=len(depend_sensors)) - 0.5) * 100
            res = minimize(
                fun=self.__total_error,
                x0=x0,
                jac=self.__phi_epsilon_sum_der,
                args=(sensor,)
            )
            phis = res.x
            for phi_j, phi_value in zip(depend_sensors, phis):
                result_phis[sensor, phi_j] = phi_value
        return result_phis

    def optimize_batch_common(self, areas: list[ChannelArea]) -> np.ndarray:
        self.__process_areas = areas
        return self.__optimize()

    def optimize_batch_individually(self, areas: list[ChannelArea]) -> list[np.ndarray]:
        result = []
        for area in areas:
            self.__process_areas = [area]
            result.append(self.__optimize())
        return result

    def optimize_area(self, area: ChannelArea) -> np.ndarray:
        return self.optimize_batch_common([area])
