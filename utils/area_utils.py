from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from vars import KMirrorSide, SurfaceType
import cv2


if TYPE_CHECKING:
    from FY3DImageArea import FY3DImageArea


def ch_area_rows_deviations(area: np.ndarray) -> list[float]:
    """Находит отклонение строк в области для одного канала"""
    h = area.shape[0]
    area_avg = area.mean()
    deviations = []
    for row_i in range(h):
        row_avg = area[row_i].mean()
        deviations.append(row_avg - area_avg)
    return deviations


def img_area_rows_deviations(area: FY3DImageArea) -> dict[int, list[float]]:
    """Находит отклонение строк в области для всех каналов
    Возвращает словарь: {
        Канал: [Отклонения датчиков]
    }
    """
    res = dict()
    for ch in range(5, 20):
        ch_area = area.get_vis_channel(ch)
        ch_deviations = ch_area_rows_deviations(ch_area)
        res[ch] = ch_deviations
    return res


def find_neighbor_areas(areas: list[FY3DImageArea]) -> list[tuple[FY3DImageArea, FY3DImageArea]]:
    """Находит и возвращает пары областей, соответствующие разным сторонам зеркала"""
    pairs = []
    areas = areas.copy()
    while areas:
        area_1 = areas.pop(0)
        for i, area_2 in enumerate(areas):

            higher_area = min(area_1, area_2, key=lambda a: a.y)
            lower_area = max(area_1, area_2, key=lambda a: a.y)

            height_10 = higher_area.height == lower_area.height == 10
            aligned_to_sides = higher_area.y % 10 == 0 and lower_area.y % 10 == 0
            on_proper_sides = (higher_area.y // 10) % 2 == 0 and (lower_area.y // 10) % 2 == 1
            are_neighbors = higher_area.y + higher_area.height == lower_area.y
            same_size = higher_area.x == lower_area.x and higher_area.width == lower_area.width
            is_valid = height_10 and aligned_to_sides and on_proper_sides and are_neighbors and same_size

            if is_valid:
                pairs.append((higher_area, lower_area))
                areas.pop(i)
                break
    return pairs


def filter_areas_by_mirror_side(areas: list[FY3DImageArea], side: int):
    """Отбираем области, снятые определённой стороной зеркала
    side:
        0 - сторона зеркала 0
        1 - сторона зеркала 1
        2 - обе стороны зеркала
    """
    if side == 2:
        return areas

    def filter_func(area):
        return (area.y // 10) % 2 == side

    filtered_areas = list(filter(lambda area: filter_func(area), areas))
    return filtered_areas


def get_area_mirror_side(y: int, height: int) -> KMirrorSide:
    if y % 10 + height > 10:
        return KMirrorSide.MIXED
    if (y // 10) % 2 == 0:
        return KMirrorSide.SIDE_1
    else:
        return KMirrorSide.SIDE_2


def mean_area_color(area: FY3DImageArea) -> tuple[int, int, int]:
    """Находит средний rgb-цвет области"""
    colored_img = np.array(area.get_colored_picture())
    mean_r = int(colored_img[:, :, 0].mean())
    mean_g = int(colored_img[:, :, 1].mean())
    mean_b = int(colored_img[:, :, 2].mean())
    return mean_r, mean_g, mean_b


def pixel_in_hsv_range(rgb_pixel, hsv_low, hsv_high) -> bool:
    pixel = np.array([[rgb_pixel]], dtype=np.uint8)
    pixel_hsv = cv2.cvtColor(pixel, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(pixel_hsv, hsv_low, hsv_high)
    return mask[0][0] == 255


def determine_surface_type(area: FY3DImageArea) -> SurfaceType:
    sea_hsv_range = [
        np.array([90, 25, 20]),
        np.array([140, 255, 100])
    ]
    snow_hsv_range = [
        np.array([0, 0, 40]),
        np.array([180, 50, 255])
    ]
    area.load_arrays()
    mean_color = mean_area_color(area)
    is_sea = pixel_in_hsv_range(mean_color, sea_hsv_range[0], sea_hsv_range[1])

    if is_sea:
        return SurfaceType.SEA
    else:
        return SurfaceType.SNOW
