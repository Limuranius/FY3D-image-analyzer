import numpy as np
import pandas as pd


class FY3DImageArea:
    x: int
    y: int
    width: int
    height: int
    name: str
    EV_1KM_RefSB: np.ndarray  # Каналы 5 - 19
    Latitude: np.ndarray
    Longitude: np.ndarray

    def __init__(self, x: int, y: int, width: int, height: int, name: str,
                 EV_1KM_RefSB: np.ndarray = None, Latitude: np.ndarray = None, Longitude: np.ndarray = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name

        self.EV_1KM_RefSB = EV_1KM_RefSB
        self.Latitude = Latitude
        self.Longitude = Longitude

    def get_vis_channel(self, channel: int) -> np.ndarray:
        """channel - канал от 5 до 19"""
        ch_i = channel - 5
        return np.float32(self.EV_1KM_RefSB[ch_i])

    def save_vis_to_excel(self, file_name: str):
        excel_writer = pd.ExcelWriter(file_name)
        for channel in range(5, 20):
            ch_area = self.get_vis_channel(channel)
            df = pd.DataFrame(ch_area)
            df.to_excel(excel_writer)
        excel_writer.close()