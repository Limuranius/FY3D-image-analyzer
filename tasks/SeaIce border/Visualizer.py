import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt
from database import FY3DImage, FY3DImageArea, ChannelArea
import noise
from vars import RESULTS_DIR
import os

sns.set_style("darkgrid")

FOLDER_NAME = "Влияние датчиков друг на друга"
if not os.path.exists(os.path.join(RESULTS_DIR, FOLDER_NAME)):
    os.mkdir(os.path.join(RESULTS_DIR, FOLDER_NAME))

class Visualizer:
    def save_noise_approximation(self,
                                 areas: list[ChannelArea],
                                 areas_phis: list[np.ndarray],
                                 name: str):
        df = pd.DataFrame(columns=["x", "noise_value", "type", "area_id", "sensor"])
        for area, phis in zip(areas, areas_phis):
            true_noise = area.true_noise
            predicted_noise = noise.area_predicted_noise(area, phis)
            for sensor in range(10):
                for x in range(area.w):
                    df.loc[len(df)] = [
                        x,
                        true_noise[sensor, x],
                        "True noise",
                        area.unique_str(),
                        sensor
                    ]
                    df.loc[len(df)] = [
                        x,
                        predicted_noise[sensor, x],
                        "Predicted noise",
                        area.unique_str(),
                        sensor
                    ]
        sns.relplot(
            data=df,
            x="x",
            y="noise_value",
            hue="type",
            col="area_id",
            row="sensor",
            kind="line",
            facet_kws={"sharex": False, "sharey": False}
        )
        path = os.path.join(RESULTS_DIR, FOLDER_NAME, name)
        plt.savefig(path, dpi=300)

    def save_individual_coeffs(self,
                               areas: list[ChannelArea],
                               areas_phis: list[np.ndarray]):
        df = pd.DataFrame(columns=["main_sensor", "sensor", "phi_value", "area_id"])
        for area, phis in zip(areas, areas_phis):
            area_id = area.unique_str()
            for main_sensor in range(10):
                for sensor in range(10):
                    phi_value = phis[main_sensor, sensor]
                    df.loc[len(df)] = [main_sensor, sensor, phi_value, area_id]
        sns.relplot(
            data=df,
            x="sensor",
            y="phi_value",
            hue="area_id",
            row="main_sensor",
            kind="line"
        )
        path = os.path.join(RESULTS_DIR, FOLDER_NAME, "INDIV_COEFFS.png")
        plt.savefig(path, dpi=300)

    def show_all(self):
        df = ch_area_to_df(self.ch_area)
        sns.relplot(
            data=df,
            x="x",
            y="value",
            hue="sensor",
            kind="line",
            palette="tab10"
        )
        path = f"{self.root_dir}/all img_id={self.img_id} y={self.y}.jpg"
        plt.savefig(path, dpi=300)
