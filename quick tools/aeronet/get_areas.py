from database import FY3DImage, FY3DImageArea
from sites import sites_positions

AREA_RADIUS = 3


def get_image_sites(image: FY3DImage) -> list[str]:
    names = []
    for site_name, site_row in sites_positions.iterrows():
        if image.contains_pos(site_row["lat"], site_row["lon"]):
            names.append(site_name)
    return names


def get_site_area(image: FY3DImage, lat: float, lon: float) -> FY3DImageArea:
    site_i, site_j = image.get_closest_pixel(lat, lon)
    x = site_j - AREA_RADIUS
    y = site_i - AREA_RADIUS
    w = h = AREA_RADIUS * 2 + 1
    area = image.get_area(x, y, w, h)
    return area


