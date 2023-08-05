import h5py
from utils.utils import *
import pandas as pd
import datetime
from database import *
from utils import getImageMonotone
import pickle

class FY3DImage(BaseModel):

    # Поля в базе данных
    path = CharField()
    name = CharField(default="")
    is_selected = BooleanField(default=False)
    is_std_map_calculated = BooleanField(default=False)
    std_sum_map = BlobField(null=True)

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
        image = get_colored_image(r, g, b)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            if area.is_selected:
                draw_rectangle(image, area.x, area.y, area.width, area.height)
        return image

    def get_vis_channel_picture(self, channel: int) -> Image:
        """Возвращает монохромное изображение определённого канала"""
        ch_i = channel - 5
        layer = self.EV_1KM_RefSB[ch_i]
        image = get_monochrome_image(layer)

        # Отмечаем границы областей на изображении
        for area in self.areas:
            if area.is_selected:
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

    def get_date(self) -> datetime.date:
        date_str = self.file_attrs["Data Creating Date"].decode()
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return date

    def get_year(self) -> int:
        return self.get_date().year

    def get_datetime(self) -> datetime.datetime:
        pass

    def calculate_std_map(self) -> None:
        std_map = getImageMonotone.calc_std_sum_map(self.EV_1KM_RefSB)
        compressed = getImageMonotone.compress_std_sum_map(std_map)
        pkl = pickle.dumps(compressed)
        self.std_sum_map = pkl
        self.is_std_map_calculated = True
        self.save()

    @classmethod
    def all_images(cls):
        return cls.select()


FY3DImage.create_table()
