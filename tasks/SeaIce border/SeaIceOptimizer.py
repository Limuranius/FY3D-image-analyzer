import os.path

import pandas as pd
from scipy.optimize import minimize
import numpy as np
from database import ChannelArea
import vars


NOISE_IGNORE_THRESHOLD = 300

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
        noises = diff * phis
        return noises.sum()

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
        return np.array([
            self.__partial_derivative(phis, 0, sensor_i),
            self.__partial_derivative(phis, 1, sensor_i),
            self.__partial_derivative(phis, 2, sensor_i),
            self.__partial_derivative(phis, 3, sensor_i),
            self.__partial_derivative(phis, 4, sensor_i),
            self.__partial_derivative(phis, 5, sensor_i),
            self.__partial_derivative(phis, 6, sensor_i),
            self.__partial_derivative(phis, 7, sensor_i),
            self.__partial_derivative(phis, 8, sensor_i),
            self.__partial_derivative(phis, 9, sensor_i),
        ])

    def __optimize(self) -> np.ndarray:
        result_phis = np.empty(shape=(10, 10), dtype=np.float_)
        for sensor in range(10):
            x0 = (np.random.random(size=10) - 0.5) * 100
            res = minimize(
                fun=self.__total_error,
                x0=x0,
                jac=self.__phi_epsilon_sum_der,
                args=(sensor,)
            )
            phis = res.x
            phis[sensor] = 0
            result_phis[sensor] = phis
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
