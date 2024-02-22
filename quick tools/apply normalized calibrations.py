import h5py
from database.FY3DImage import FY3DImage
import tqdm
import numpy as np
import os
import vars

ch_8_norm_devs = np.array([
    -1.74109818,
    -1.557777617,
    -1.199189389,
    -0.273102157,
    0.598164957,
    0.886090404,
    1.172219734,
    0.966471818,
    0.896550729,
    0.251669702
])
ch_8_norm_devs.resize((10, 1))

CHANNEL = 8
CH_I = CHANNEL - 5
IMG_ID = 119
image = FY3DImage.get(id=IMG_ID).EV_1KM_RefSB[CH_I, :, :]

HEIGHT = 2000
WIDTH = 2048


def calibrate_mean10():
    with tqdm.tqdm(total=HEIGHT * WIDTH, desc="Calibrating image") as pbar:
        for y in range(0, HEIGHT, 10):
            row10 = image[y: y + 10]
            col_means = row10.mean(axis=0)
            row10_devs = row10 - col_means
            col_abs_mean_devs = np.abs(row10_devs).mean(axis=0)

            cal_deviations = ch_8_norm_devs * col_abs_mean_devs
            image[y: y + 10] = row10 - cal_deviations

            pbar.update(WIDTH * 10)

    with h5py.File(os.path.join(vars.RESULTS_DIR, "Normally calibrated.hdf"), "w") as f:
        f.create_dataset("EV_1KM_RefSB", data=image)


calibrate_mean10()

