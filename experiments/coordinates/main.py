import h5py
import matplotlib.pyplot as plt
import numpy as np
from utils import math_utils
from database import FY3DImage
from global_land_mask import globe
from scipy.interpolate import RegularGridInterpolator
import tqdm
import cv2


def enhance_coord_2(arr: np.ndarray):
    h, w = arr.shape
    enhanced = np.zeros((2000, 2048))
    for i in tqdm.trange(h - 1):
        for j in range(w - 1):
            values = arr[i: i+2, j: j+2]
            interp_values = interpolate_box(values, (6, 6))
            enhanced[i * 5: (i + 1) * 5 + 1, j * 5: (j + 1) * 5 + 1] = interp_values
    return enhanced


def find_mask_img_coords_enhance(img: FY3DImage):
    lat_grid = img.Latitude[:, :].astype(float)
    lon_grid = img.Longitude[:, :].astype(float)
    # lat_enhance = enhance_coord_2(lat_grid)
    # lon_enhance = enhance_coord_2(lon_grid)
    lat_enhance = math_utils.interpolate_matrix(lat_grid, new_size=(2000, 2048))
    lon_enhance = math_utils.interpolate_matrix(lon_grid, new_size=(2000, 2048))
    return globe.is_land(lat_enhance, lon_enhance)


def find_mask_geo_coords(geo_path: str):
    with h5py.File(geo_path, "r") as file:
        geolocation = file["Geolocation"]
        Latitude = geolocation["Latitude"][:, :].astype(float)
        Longitude = geolocation["Longitude"][:, :].astype(float)
        return globe.is_land(Latitude, Longitude)


def find_mask_ch15_threshold(img: FY3DImage):
    channel15 = img.get_vis_channel(15)
    return channel15 > 1000


def find_mask_3(img: FY3DImage):
    lat_grid = img.Latitude
    lon_grid = img.Longitude
    lat_grid_full = np.empty(shape=(2000, 2048))
    lat_grid_full[::5, ::5] = lat_grid
    lon_grid_full = np.empty(shape=(2000, 2048))
    lon_grid_full[::5, ::5] = lon_grid
    return globe.is_land(lat_grid_full, lon_grid_full)


def find_mask_4(img: FY3DImage):
    lat_grid = img.Latitude
    lon_grid = img.Longitude
    return globe.is_land(lat_grid, lon_grid)


def find_mask_5(img: FY3DImage):
    channel15 = img.get_vis_channel(15)
    mask = channel15 > 1000
    mask_small = mask[::5, ::5]
    return mask_small


# for ID in [5, 38, 74, 119]:
#     img: FY3DImage = FY3DImage.get(id=ID)
#
#     mask1 = find_mask_img_coords_enhance(img)
#     mask2 = find_mask_ch15_threshold(img)
#     mask3 = mask1 ^ mask2
#
#     # fig, (ax1, ax2, ax3) = plt.subplots(ncols=3)
#     # ax1.imshow(mask1)
#     # ax2.imshow(mask2)
#     # ax3.imshow(mask3)
#     # plt.show()
#
#     # plt.imshow(mask3)
#     # plt.savefig("mask.jpg", dpi=300)
#     cv2.imwrite(f"{ID}.jpg", mask3.astype(np.uint8) * 255)

img: FY3DImage = FY3DImage.get(id=2)
# mask1 = find_mask_geo_coords(r"D:\Снимки со спутников\17.03.23 06.20 (Берег Австралии)\FY3D_MERSI_GBAL_L1_20230317_0620_GEO1K_MS.HDF")
mask1 = find_mask_ch15_threshold(img)
mask2 = find_mask_img_coords_enhance(img)
mask3 = mask1 ^ mask2

plt.imshow(mask3)
plt.show()

# cv2.imwrite(f"geo.jpg", mask3.astype(np.uint8) * 255)
