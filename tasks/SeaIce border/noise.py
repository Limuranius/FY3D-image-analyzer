import numpy as np
from database import ChannelArea


def area_true_noise(area: ChannelArea) -> np.ndarray:
    noise = area.to_numpy().copy()
    noise[area.sea_mask] -= area.sea_value
    noise[~area.sea_mask] -= area.ice_value
    return noise


def area_predicted_noise(
        area: ChannelArea,
        phis: np.ndarray
) -> np.ndarray:

    ch_area = area.to_numpy()
    noise = np.empty_like(ch_area, dtype=np.float_)
    for sensor_i in range(area.h):
        diff = ch_area[sensor_i] - ch_area
        sensor_phis = phis[sensor_i]
        for j in range(area.w):
            diff_col = diff[:, j]
            col_noises = diff_col * sensor_phis
            noise[sensor_i, j] = col_noises.sum()
    return noise
