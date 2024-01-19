import numpy as np
import pandas as pd
from database import FY3DImage
import vars
import os
import h5py

coeffs = pd.read_pickle(os.path.join(vars.RESULTS_DIR, "common_coeffs.pkl"))

IMG_ID = 119
image = FY3DImage.get(id=IMG_ID).EV_1KM_RefSB[3, :, :]
new_image = np.empty_like(image)

height = 2000
width = 2048

for y in range(height):
    sensor = y % 10
    sensor_coeffs = coeffs[sensor]
    block_y = (y // 10) * 10
    block = image[block_y:block_y+10].astype(np.int_)
    diff = block[sensor] - block
    noises = diff * sensor_coeffs.reshape(10, 1)
    predicted_noise = noises.sum(axis=0)
    new_image[y] = image[y] - predicted_noise

with h5py.File(os.path.join(vars.RESULTS_DIR, "calibrated.hdf"), "w") as f:
    f.create_dataset("EV_1KM_RefSB", data=new_image)
with h5py.File(os.path.join(vars.RESULTS_DIR, "before_calibration.hdf"), "w") as f:
    f.create_dataset("EV_1KM_RefSB", data=image)