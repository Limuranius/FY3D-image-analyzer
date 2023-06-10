import h5py
from FY3DImageArea import FY3DImageArea
from utils.utils import *
import os
import pandas as pd
from datetime import datetime

from vars import SurfaceType


class FY3DImage:
    areas: list[FY3DImageArea]
    name: str

    def __init__(self, path: str, name: str = ""):
        self.name = name
        self.areas = []

        self.file = h5py.File(path, "r")
        self.file_attrs = self.file.attrs
        geolocation = self.file["Geolocation"]
        self.Latitude = geolocation["Latitude"]
        self.Longitude = geolocation["Longitude"]
        self.height, self.width = self.Longitude.shape

        data = self.file["Data"]
        self.EV_1KM_Emissive = data["EV_1KM_Emissive"]
        self.EV_1KM_RefSB = data["EV_1KM_RefSB"]
        self.EV_250_Aggr1KM_Emissive = data["EV_250_Aggr.1KM_Emissive"]
        self.EV_250_Aggr1KM_RefSB = data["EV_250_Aggr.1KM_RefSB"]

        calibration = self.file["Calibration"]
        self.BB_DN_average = calibration["BB_DN_average"]
        self.SV_DN_average = calibration["SV_DN_average"]
        self.VOC_DN_average = calibration["VOC_DN_average"]
        self.VIS_Cal_Coeff = calibration["VIS_Cal_Coeff"]

    def get_area(self, x: int, y: int, width: int, height: int,
                 surface_type: SurfaceType = SurfaceType.UNKNOWN) -> FY3DImageArea:
        name = os.path.join(self.name, f"{x} {y} {width} {height}")
        return FY3DImageArea(
            x, y, width, height, name,
            EV_1KM_RefSB=self.EV_1KM_RefSB[:, y: y + height, x: x + width],
            Latitude=self.Latitude[y: y + height, x: x + width],
            Longitude=self.Longitude[y: y + height, x: x + width],
            surface_type=surface_type
        )

    def add_area(self, x: int, y: int, width: int, height: int,
                 surface_type: SurfaceType = SurfaceType.UNKNOWN):
        self.areas.append(self.get_area(x, y, width, height, surface_type))

    def get_center_coords(self) -> tuple[float, float]:
        """Возвращает широту и долготу центрального пикселя"""
        x = self.width // 2
        y = self.height // 2
        lat = self.Latitude[y, x]
        long = self.Longitude[y, x]
        return lat, long

    def get_colored_picture(self) -> Image:
        """Возвращает цветное изображение, состоящее из каналов 3, 2 и 1"""
        r = self.EV_250_Aggr1KM_RefSB[2]  # 3 канал
        g = self.EV_250_Aggr1KM_RefSB[1]  # 2 канал
        b = self.EV_250_Aggr1KM_RefSB[0]  # 1 канал
        image = get_colored_image(r, g, b)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            draw_rectangle(image, area.x, area.y, area.width, area.height)
        return image

    def get_vis_channel_picture(self, channel: int) -> Image:
        """Возвращает монохромное изображение определённого канала"""
        ch_i = channel - 5
        layer = self.EV_1KM_RefSB[ch_i]
        image = get_monochrome_image(layer)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            draw_rectangle(image, area.x, area.y, area.width, area.height)
        return image

    def get_name(self):
        return self.name

    def save_to_excel(self, file_name: str):
        writer = pd.ExcelWriter(file_name)
        for ch in range(5, 20):
            sheet_data = []
            for area in self.areas:
                ch_area = area.get_vis_channel(ch)
                sheet_data += [[area.get_short_name()]]
                sheet_data += ch_area.tolist()
                sheet_data += [[]]
                sheet_data += [[]]
                sheet_data += [[]]
            pd.DataFrame(sheet_data).to_excel(writer, f"Канал {ch}", index_label=False, index=False)
        writer.close()

    def get_date(self) -> datetime:
        date_str = self.file_attrs["Data Creating Date"].decode()
        date = datetime.strptime(date_str, "%Y-%m-%d")
        return date

    def get_year(self) -> int:
        return self.get_date().year
