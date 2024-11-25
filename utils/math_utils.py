import numpy as np
from scipy.interpolate import RegularGridInterpolator
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature


def interpolate_matrix(arr: np.ndarray, new_size: tuple[int, int]):
    new_h, new_w = new_size
    h, w = arr.shape
    x = np.linspace(0, new_w - 1, num=w)
    y = np.linspace(0, new_h - 1, num=h)
    interp = RegularGridInterpolator((y, x), arr[:, :], method="linear")
    X, Y = np.meshgrid(list(range(new_w)), list(range(new_h)))
    enhanced = interp((Y, X))
    return enhanced


def interpolate_box(values, output_size):
    x = [0, 1]
    y = [0, 1]
    interp = RegularGridInterpolator((y, x), values)
    new_x = np.linspace(0, 1, num=output_size[1])
    new_y = np.linspace(0, 1, num=output_size[0])
    X, Y = np.meshgrid(new_x, new_y)
    return interp((Y, X))


def geopoint_inside_polygon(
        point: tuple[float, float],
        polygon: list[tuple[float, float]]
) -> bool:
    point = Feature(geometry=Point(point))
    polygon = Polygon([polygon])
    return boolean_point_in_polygon(point, polygon)
