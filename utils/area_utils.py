from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
from scipy.ndimage import median_filter, convolve
import cv2

from vars import KMirrorSide, SurfaceType
import pandas as pd


if TYPE_CHECKING:
    from database.FY3DImageArea import FY3DImageArea
    from database import ChannelArea


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


def get_area_mirror_side(y: int, height: int = 1) -> KMirrorSide:
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


def determine_surface_type(area: FY3DImageArea) -> SurfaceType:
    VALUE_THRESHOLD = 1000
    STD_THRESHOLD = 500
    channel = 13

    ch_area = area.get_vis_channel(channel)
    mean_value = ch_area.mean()
    std = ch_area.std()

    if std > STD_THRESHOLD:
        return SurfaceType.MIXED
    elif mean_value < VALUE_THRESHOLD:
        return SurfaceType.SEA
    else:
        return SurfaceType.SNOW



def ch_area_to_df(ch_area: np.ndarray):
    df = pd.DataFrame(columns=["sensor", "x", "value"])
    for sensor in range(10):
        row = ch_area[sensor]
        for x, value in enumerate(row):
            df.loc[len(df)] = [sensor, x, value]
    return df


def ch_area_to_median(ch_area: np.ndarray, kernel=(1, 20)):
    median_area = median_filter(ch_area, size=kernel)
    return median_area


def find_two_peaks(ch_area: np.ndarray) -> tuple[int, int]:
    hist_y, hist_x = np.histogram(ch_area, bins=int(ch_area.max() - ch_area.min() + 1))
    hist_x = (hist_x[:-1] + hist_x[1:]) / 2
    med = np.median(hist_x)
    left_max_i = hist_y[hist_x <= med].argmax()
    right_max_i = hist_y[hist_x > med].argmax()
    return int(hist_x[left_max_i]), int(hist_x[hist_x > med][right_max_i])


# def ch_area_to_sea_mask(ch_area: np.ndarray):
#     median = ch_area_to_median(ch_area)
#     sea_value, ice_value = find_two_peaks(median)
#     sea_dist = np.abs(ch_area - sea_value)
#     ice_dist = np.abs(ch_area - ice_value)
#     sea_mask = sea_dist < ice_dist
#     return sea_mask


# def ch_area_to_sea_mask(ch_area: np.ndarray):
#     kernel = np.array([[1, 0, -1]])
#     conv_area = convolve(ch_area, kernel, mode="valid")
#     threshold_coords = conv_area.argmax(axis=1)
#     threshold_coords += 1
#     sea_mask = ch_area.copy().astype(np.bool_)
#     for sensor, thresh_x in enumerate(threshold_coords):
#         sea_mask[sensor, :thresh_x] = True
#         sea_mask[sensor, thresh_x:] = False
#     return sea_mask


def ch_area_to_sea_mask(ch_area: np.ndarray):
    sea_value, ice_value = find_two_peaks(ch_area)
    sea_mask = np.abs(ch_area - sea_value) < np.abs(ch_area - ice_value)
    return sea_mask


# def ch_area_to_sea_mask(ch_area: np.ndarray):
#     sea_value, ice_value = find_two_peaks(ch_area)
#     threshold = sea_value * 1.5
#     sea_mask = ch_area < threshold
#     return sea_mask


def ch_area_to_deviations(ch_area: np.ndarray):
    median = ch_area_to_median(ch_area)
    sea_mask = ch_area_to_sea_mask(median)
    sea_value, ice_value = find_two_peaks(median)
    res = ch_area.copy().astype(np.int32)
    res[sea_mask] -= sea_value
    res[~sea_mask] -= ice_value
    return res


def get_border_mask(area: ChannelArea, width: int) -> np.ndarray:
    """Возвращает маску, где True - граница между льдом и водой"""
    sobel_kernel = np.array([[-1, 1]])
    border = convolve(area.sea_mask, sobel_kernel)
    dilate_kernel = np.ones((1, width * 2 + 1))
    thick_border = cv2.dilate(border.astype(np.uint8), dilate_kernel)
    return thick_border.astype(np.bool_)


def remove_border_values(area: ChannelArea) -> ChannelArea:
    """Returns area with removed n pixels of sea_ice border"""
    from database import ChannelArea

    REMOVE_RADIUS = 5

    border_mask = get_border_mask(area, REMOVE_RADIUS)

    new_charea = []
    for i in range(10):
        row = area.to_numpy()[i][~border_mask[i]]
        new_charea.append(row)
    new_charea = np.array(new_charea)
    new_area = ChannelArea.from_ndarray(new_charea, channel=area.channel)
    new_area.parent = area.parent
    return new_area
