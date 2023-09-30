from __future__ import annotations
import h5py
from utils import some_utils
from utils import getImageMonotone
import pandas as pd
import datetime
from database import *
import pickle
from PIL import Image
import numpy as np
import vars
import typing


class FY3DImage(BaseModel):
    # Поля в базе данных
    path = CharField()
    name = CharField(default="")
    is_selected = BooleanField(default=False)
    is_std_map_calculated = BooleanField(default=False)
    std_sum_map = BlobField(null=True)
    year = IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = h5py.File(self.path, "r")
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
        image = some_utils.get_colored_image(r, g, b)
        image = some_utils.increase_brightness(image, 50)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            if area.is_selected:
                match area.surface_type:
                    case vars.SurfaceType.UNKNOWN.value:
                        color = "#FF0000"
                    case vars.SurfaceType.SNOW.value:
                        color = "#00FF00"
                    case vars.SurfaceType.SEA.value:
                        color = "#0000FF"
                some_utils.draw_rectangle(image, area.x, area.y, area.width, area.height, color)
        return image

    def get_preview(self) -> Image:
        compress_factor = vars.PREVIEW_COMPRESS_FACTOR
        r = self.EV_250_Aggr1KM_RefSB[2][0:2000:compress_factor, 0:2048:compress_factor]  # 3 канал
        g = self.EV_250_Aggr1KM_RefSB[1][0:2000:compress_factor, 0:2048:compress_factor]  # 2 канал
        b = self.EV_250_Aggr1KM_RefSB[0][0:2000:compress_factor, 0:2048:compress_factor]  # 1 канал

        image = some_utils.get_colored_image(r, g, b)
        image = some_utils.increase_brightness(image)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            if area.is_selected:
                match area.surface_type:
                    case vars.SurfaceType.UNKNOWN.value:
                        color = "#FF0000"
                    case vars.SurfaceType.SNOW.value:
                        color = "#00FF00"
                    case vars.SurfaceType.SEA.value:
                        color = "#0000FF"
                some_utils.draw_rectangle(image, area.x // compress_factor, area.y // compress_factor,
                                          area.width // compress_factor, area.height // compress_factor, color)
        return image

    def get_vis_channel_picture(self, channel: int) -> Image:
        """Возвращает монохромное изображение определённого канала"""
        ch_i = channel - 5
        layer = self.EV_1KM_RefSB[ch_i]
        image = some_utils.get_monochrome_image(layer)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            if area.is_selected:
                some_utils.draw_rectangle(image, area.x, area.y, area.width, area.height)
        return image

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

    def get_date(self) -> datetime.date:
        date_str = self.file_attrs["Data Creating Date"].decode()
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return date

    def get_year(self) -> int:
        return self.get_date().year

    def get_datetime(self) -> datetime.datetime:
        date_str = self.file_attrs["Data Creating Date"].decode()
        time_str = self.file_attrs["Data Creating Time"].decode().split(".")[0]
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.datetime.strptime(time_str, "%H:%M:%S").time()
        dt = datetime.datetime.combine(date, time)
        return dt

    def calculate_std_map(self) -> None:
        std_map = getImageMonotone.calc_std_sum_map_gpu(self.EV_1KM_RefSB)
        compressed = getImageMonotone.compress_std_sum_map(std_map)
        pkl = pickle.dumps(compressed)
        self.std_sum_map = pkl
        self.is_std_map_calculated = True
        self.save()

    def get_vis_channel(self, channel: int) -> np.ndarray:
        """channel - канал от 5 до 19"""
        ch_i = channel - 5
        return np.uint16(self.EV_1KM_RefSB[ch_i])

    def selected_areas(self):
        import FY3DImageArea
        return self.areas.where(FY3DImageArea.FY3DImageArea.is_selected == True)

    def get_area(self, x, y, w, h):
        import FY3DImageArea
        return FY3DImageArea.FY3DImageArea(x=x, y=y, width=w, height=h, image=self)

    def get_unique_name(self) -> str:
        dt_fmt = "%d-%m-%Y %H.%M"
        return f"{self.name} ({self.get_datetime().strftime(dt_fmt)})"

    @classmethod
    def all_images(cls) -> typing.Iterable[FY3DImage]:
        return cls.select()

FY3DImage.create_table()
