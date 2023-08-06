import numpy as np
import pandas as pd
from vars import SurfaceType, KMirrorSide
import os
from database import *
from FY3DImage import FY3DImage
from utils import some_utils
from PIL import Image


class FY3DImageArea(BaseModel):
    # Поля в базе данных
    x = IntegerField()
    y = IntegerField()
    width = IntegerField()
    height = IntegerField()
    surface_type = IntegerField(default=SurfaceType.UNKNOWN.value)
    k_mirror_side = IntegerField()
    image = ForeignKeyField(FY3DImage, backref="areas")
    is_selected = BooleanField(default=True)

    EV_1KM_RefSB: np.ndarray  # Каналы 5 - 19
    EV_250_Aggr1KM_RefSB: np.ndarray  # Каналы 1 - 3
    Latitude: np.ndarray
    Longitude: np.ndarray

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.y % 10 + self.height > 10:
            self.k_mirror_side = KMirrorSide.MIXED.value
        if (self.y // 10) % 2 == 0:
            self.k_mirror_side = KMirrorSide.SIDE_1.value
        else:
            self.k_mirror_side = KMirrorSide.SIDE_2.value

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

    def load_arrays(self):
        self.EV_1KM_RefSB = self.image.EV_1KM_RefSB[:, self.y: self.y + self.height, self.x: self.x + self.width]
        self.EV_250_Aggr1KM_RefSB = self.image.EV_250_Aggr1KM_RefSB[:, self.y: self.y + self.height, self.x: self.x + self.width]
        self.Latitude = self.image.Latitude[self.y: self.y + self.height, self.x: self.x + self.width]
        self.Longitude = self.image.Longitude[self.y: self.y + self.height, self.x: self.x + self.width]

    def get_colored_picture(self) -> Image:
        r = self.EV_250_Aggr1KM_RefSB[2]  # 3 канал
        g = self.EV_250_Aggr1KM_RefSB[1]  # 2 канал
        b = self.EV_250_Aggr1KM_RefSB[0]  # 1 канал
        image = some_utils.get_colored_image(r, g, b)
        return image


FY3DImageArea.create_table()
