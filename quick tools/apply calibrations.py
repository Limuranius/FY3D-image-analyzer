import pandas as pd
import h5py
from database.FY3DImage import FY3DImage
from utils.area_utils import get_area_mirror_side
import tqdm
import vars
import numpy as np
import os

coeffs = pd.read_pickle(os.path.join(vars.RESULTS_DIR, "cal_coeffs.pkl"))

# image_path = r"D:\Снимки со спутников\17.03.23 06.20 (Берег Австралии)\FY3D_MERSI_GBAL_L1_20230317_0620_1000M_MS.HDF"
# image_path = r"D:\Снимки со спутников\Белые снимки\FY3D_MERSI_GBAL_L1_20230115_2135_1000M_MS.HDF"
image_path = r"D:\Снимки со спутников\Белые снимки\FY3D_MERSI_GBAL_L1_20230121_2125_1000M_MS.HDF"

image = FY3DImage(path=image_path).EV_1KM_RefSB[:, :, :]

height = 2000
width = 2048

with tqdm.tqdm(total=15 * height * width, desc="Calibrating image") as pbar:
    for channel in range(5, 20):
        ch_i = channel - 5
        for y in range(height):
            sensor = y % 10
            coeff = coeffs[(coeffs["channel"] == channel) & (coeffs["sensor"] == sensor)
                           & (coeffs["k_mirror_side"] == get_area_mirror_side(y).value)].squeeze()
            slope = coeff["slope"]
            intercept = coeff["intercept"]

            row_values = image[ch_i, y]
            deviation = row_values * slope + intercept
            calibrated_row_values = row_values - deviation
            calibrated_row_values = np.maximum(calibrated_row_values, 0)
            image[ch_i, y] = np.rint(calibrated_row_values)
            pbar.update(width)

with h5py.File(os.path.join(vars.RESULTS_DIR, "calibrated (Белый снимок 2125).hdf"), "w") as f:
    f.create_dataset("EV_1KM_RefSB", data=image)
