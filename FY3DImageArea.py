import numpy as np
import pandas as pd
from vars import SurfaceType, KMirrorSide
import os
from database import *
import FY3DImage
from utils import some_utils
from PIL import Image
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class CacheAreaData:
    EV_1KM_RefSB: np.ndarray = None
    EV_250_Aggr1KM_RefSB: np.ndarray = None
    Latitude: np.ndarray = None
    Longitude: np.ndarray = None


class FY3DImageArea(BaseModel):
    # Поля в базе данных
    x = IntegerField()
    y = IntegerField()
    width = IntegerField()
    height = IntegerField()
    surface_type = IntegerField(default=SurfaceType.UNKNOWN.value)
    k_mirror_side = IntegerField(null=False)
    image = ForeignKeyField(FY3DImage.FY3DImage, backref="areas")
    is_selected = BooleanField(default=True)
    are_deviations_calculated = BooleanField(default=False)

    cached_data: dict[int, CacheAreaData] = defaultdict(CacheAreaData)  # id: data

    def get_vis_channel(self, channel: int) -> np.ndarray:
        """channel - канал от 5 до 19"""
        ch_i = channel - 5
        return np.uint16(self.EV_1KM_RefSB[ch_i])

    def save_vis_to_excel(self, file_name: str):
        excel_writer = pd.ExcelWriter(file_name)
        for channel in range(5, 20):
            ch_area = self.get_vis_channel(channel)
            df = pd.DataFrame(ch_area)
            df.to_excel(excel_writer)
        excel_writer.close()

    def get_global_coords(self, x: int, y: int) -> tuple[int, int]:
        return (
            self.x + x,
            self.y + y
        )

    def get_short_name(self):
        """Возвращает имя области в формате x=... y=... w=... h=..."""
        return f"x={self.x} y={self.y} w={self.width} h={self.height}"

    def get_grayscale_ch_img(self, channel: int):
        ch_area = self.get_vis_channel(channel)
        img = some_utils.get_monochrome_image(ch_area)
        return img

    def save_channels_img_to_dir(self, dir_path: str):
        for channel in range(5, 20):
            img = self.get_grayscale_ch_img(channel)
            path = os.path.join(dir_path, f"{channel}.jpg")
            img.save(path)

    def get_surface_type(self) -> SurfaceType:
        return SurfaceType(self.surface_type)

    def get_mirror_side(self) -> KMirrorSide:
        return KMirrorSide(self.k_mirror_side)

    def get_colored_picture(self) -> Image:
        r = self.EV_250_Aggr1KM_RefSB[2]  # 3 канал
        g = self.EV_250_Aggr1KM_RefSB[1]  # 2 канал
        b = self.EV_250_Aggr1KM_RefSB[0]  # 1 канал
        image = some_utils.get_colored_image(r, g, b)
        return image

    @property
    def EV_1KM_RefSB(self):
        if FY3DImageArea.cached_data[self.id].EV_1KM_RefSB is None:
            area = self.image.EV_1KM_RefSB[:, self.y: self.y + self.height, self.x: self.x + self.width]
            FY3DImageArea.cached_data[self.id].EV_1KM_RefSB = area
        return FY3DImageArea.cached_data[self.id].EV_1KM_RefSB

    @property
    def EV_250_Aggr1KM_RefSB(self):
        if FY3DImageArea.cached_data[self.id].EV_250_Aggr1KM_RefSB is None:
            area = self.image.EV_250_Aggr1KM_RefSB[:, self.y: self.y + self.height, self.x: self.x + self.width]
            FY3DImageArea.cached_data[self.id].EV_250_Aggr1KM_RefSB = area
        return FY3DImageArea.cached_data[self.id].EV_250_Aggr1KM_RefSB

    @property
    def Latitude(self):
        if FY3DImageArea.cached_data[self.id].Latitude is None:
            area = self.image.Latitude[:, self.y: self.y + self.height, self.x: self.x + self.width]
            FY3DImageArea.cached_data[self.id].Latitude = area
        return FY3DImageArea.cached_data[self.id].Latitude

    @property
    def Longitude(self):
        if FY3DImageArea.cached_data[self.id].Longitude is None:
            area = self.image.Longitude[:, self.y: self.y + self.height, self.x: self.x + self.width]
            FY3DImageArea.cached_data[self.id].Longitude = area
        return FY3DImageArea.cached_data[self.id].Longitude


FY3DImageArea.create_table()
