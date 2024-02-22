import os.path
import pickle
import numpy as np
from vars import INDIV_COEFFS_FILE_PATH, COMMON_COEFFS_FILE_PATH
from database import ChannelArea
from SeaIceOptimizer import SeaIceOptimizer
from Visualizer import Visualizer
from tqdm import tqdm
from utils.area_utils import remove_border_values


class OptimizerVisualizer:
    __areas: list[ChannelArea]
    __channel: int

    def __init__(self,
                 areas: list[ChannelArea],
                 channel: int):
        self.__areas = areas
        self.__channel = channel

    def calculate_individual_coefficients(self) -> None:
        # if os.path.exists(INDIV_COEFFS_FILE_PATH):
        #     with open(INDIV_COEFFS_FILE_PATH, "rb") as f:
        #         indiv_coeffs = pickle.load(f)
        # else:
        #     indiv_coeffs = dict()

        optimizer = SeaIceOptimizer()
        coeffs = optimizer.optimize_batch_individually(self.__areas)
        indiv_coeffs = {area.unique_str(): phis for area, phis in zip(self.__areas, coeffs)}

        # for area in tqdm(self.__areas):
        #     if area.unique_str() not in indiv_coeffs:
        #         indiv_coeffs[area.unique_str()] = optimizer.optimize_area(area)
        with open(INDIV_COEFFS_FILE_PATH, "wb") as f:
            pickle.dump(indiv_coeffs, f)

    def calculate_common_coefficients(self) -> None:
        optimizer = SeaIceOptimizer()
        common_coeffs = optimizer.optimize_batch_common(self.__areas)
        with open(COMMON_COEFFS_FILE_PATH, "wb") as f:
            pickle.dump(common_coeffs, f)

    def get_individual_coefficients(self) -> dict[str, np.ndarray]:
        with open(INDIV_COEFFS_FILE_PATH, "rb") as f:
            return pickle.load(f)

    def get_common_coefficients(self) -> np.ndarray:
        with open(COMMON_COEFFS_FILE_PATH, "rb") as f:
            return pickle.load(f)

    def save_individual_approximation(self):
        visualizer = Visualizer()
        areas_phis = self.get_individual_coefficients()
        areas_phis = [areas_phis[area.unique_str()] for area in self.__areas]
        visualizer.save_noise_approximation(
            areas=self.__areas,
            areas_phis=areas_phis,
            name="INDIV_APPROX.png"
        )

    def save_common_approximation(self):
        visualizer = Visualizer()
        common_phis = self.get_common_coefficients()
        areas_phis = [common_phis] * len(self.__areas)
        visualizer.save_noise_approximation(
            areas=self.__areas,
            areas_phis=areas_phis,
            name="COMMON_APPROX.png"
        )

    def save_indiv_coeffs(self):
        visualizer = Visualizer()
        areas_phis = self.get_individual_coefficients()
        areas_phis = [areas_phis[area.unique_str()] for area in self.__areas]
        visualizer.save_individual_coeffs(
            areas=self.__areas,
            areas_phis=areas_phis
        )

    def save_common_coeffs(self):
        visualizer = Visualizer()
        phis = self.get_common_coefficients()
        visualizer.save_common_coeffs(phis)

    def validate_approximations(self):
        import noise
        optimizer = SeaIceOptimizer()
        areas_coeffs = optimizer.optimize_batch_individually(self.__areas)
        predicted_noises = []
        for area, phis in zip(self.__areas, areas_coeffs):
            pred_noise = noise.area_predicted_noise(area, phis)
            predicted_noises.append(pred_noise)

        visualizer = Visualizer()
        visualizer.save_noise_approximation(
            areas=self.__areas,
            areas_phis=areas_coeffs,
            name="(VALIDATE) INDIV APPROX ORIGINAL.png"
        )

        areas_predicted_true_noise = self.__areas
        for area, predicted_noise in zip(areas_predicted_true_noise, predicted_noises):
            area.true_noise = predicted_noise
        areas_coeffs_2 = optimizer.optimize_batch_individually(areas_predicted_true_noise)

        visualizer.save_noise_approximation(
            areas=areas_predicted_true_noise,
            areas_phis=areas_coeffs_2,
            name="(VALIDATE) INDIV APPROX TRUE PREDICTED.png"
        )

    def optimize_cut_borders(self):
        cut_areas = [remove_border_values(area) for area in self.__areas]
        optimizer = SeaIceOptimizer()
        areas_coeffs = optimizer.optimize_batch_individually(cut_areas)
        visualizer = Visualizer()
        visualizer.save_noise_approximation(
            areas=cut_areas,
            areas_phis=areas_coeffs,
            name="(CUT BORDERS) INDIV APPROX.png"
        )
