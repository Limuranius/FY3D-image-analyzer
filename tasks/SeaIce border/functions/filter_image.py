import numpy as np
import pandas as pd
from database import FY3DImage
import h5py
import timeresults

COEFFS_PATH = "coeffs.pkl"
BEFORE_CALIBRATE_PATH = timeresults.get_session_path("before_calibration.hdf")
CALIBRATED_PATH = timeresults.get_session_path("calibrated.hdf")


def filter_area(
        area: np.ndarray,
        coeffs: np.ndarray
) -> np.ndarray:
    A = coeffs[:, 0:10]
    B1 = coeffs[:, 10: 20]
    B2 = coeffs[:, 20: 30]

    height, width = area.shape
    new_area = np.empty_like(area)

    for y in range(height):
        sensor = y % 10
        block_y = (y // 10) * 10
        block = area[block_y:block_y + 10].astype(np.int_)
        diff = block[sensor] - block
        noises = diff * A[sensor].reshape(10, 1)
        predicted_noise = noises.sum(axis=0)
        b1 = B1[sensor][sensor]
        b2 = B2[sensor][sensor]
        new_area[y] = area[y] * b1 + b2 - predicted_noise

    return new_area


def main():
    coeffs = pd.read_pickle(COEFFS_PATH)
    IMG_ID = 119
    image = FY3DImage.get(id=IMG_ID).EV_1KM_RefSB[3, :, :]
    new_image = filter_area(image, coeffs)

    with h5py.File(CALIBRATED_PATH, "w") as f:
        f.create_dataset("EV_1KM_RefSB", data=new_image)
    with h5py.File(BEFORE_CALIBRATE_PATH, "w") as f:
        f.create_dataset("EV_1KM_RefSB", data=image)


if __name__ == "__main__":
    main()
