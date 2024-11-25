import math

from utils.some_utils import DN_to_Ref
from database import FY3DImageArea, FY3DImage
import get_areas
import sites

# 2 5 10 14 19 21 38 62 74 107

E0 = {
    1: 2017.963,
    2: 1828.387,
    3: 1554.807,
    4: 952.4935,
    5: 363.0785,
    6: 232.4188,
    7: 97.018,
    8: 1700.734,
    9: 1903.334,
    10: 1968.184,
    11: 1830.053,
    12: 1504.914,
    13: 1399.233,
    14: 1277.788,
    15: 955.2415,
    16: 884.8099,
    17: 828.4215,
    18: 820.4936,
    19: 680.8728,
}


def calculate_area_value(area: FY3DImageArea, channel: int):
    DN = area.get_vis_channel(channel).mean()
    # DN -= area.get_black_body_value(channel)
    Ref = DN_to_Ref(DN, area.image, channel)
    Ltoa = Ref * E0[channel] / math.pi
    return Ltoa


def calculate_site_value(image: FY3DImage, channel: int, site_name: str):
    d = {
        3: 667,
        8: 412,
        10: 490,
        12: 667,
    }
    site_data = sites.get_image_site_data(site_name, image)
    nm = d[channel]
    return float(site_data[f"Lt_mean[{nm}nm]"])
