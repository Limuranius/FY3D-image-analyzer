import h5py
import matplotlib.pyplot as plt
import numpy as np
import tqdm
from database import FY3DImage
import ch12_utils

COEFFS_PATH = "data/new_coeffs.txt"
# COEFFS_PATH = "data/manual_coeffs.txt"


def filter_area(area, coeffs: list[float], win_sizes: list[int]):
    new_area = np.empty_like(area)

    for y, row in tqdm.tqdm(enumerate(area)):
        sensor = y % 10

        row_noise = ch12_utils.predict_noise(
            row,
            coeffs[sensor],
            win_sizes[sensor]
        )

        new_area[y] = row - row_noise

    return new_area


def test():
    from ch12_utils.some_utils import change_contrast
    Y = 410
    X = 390
    WIDTH = 40
    img = FY3DImage.get(id=119)
    ch_img = img.get_vis_channel(12).astype(int)
    area = ch_img[Y: Y + 10, X: X + WIDTH]
    print(*map(int, avg_filter([area[4]], window_size=7)[0]), sep="\t")

    fig, (ax1, ax2) = plt.subplots(ncols=2)
    ax1.imshow(change_contrast(area, 300, 700), cmap="gray")
    ax2.imshow(change_contrast(filter_area(area), 300, 700), cmap="gray")
    plt.show()


def main():
    image = FY3DImage.get(id=119).EV_1KM_RefSB[7, :, :].astype(int)

    win_sizes = []
    coeffs = []
    with open(COEFFS_PATH) as f:
        for line in f:
            win_size, coeff = line.split()
            win_size = int(win_size)
            coeff = float(coeff)
            win_sizes.append(win_size)
            coeffs.append(coeff)

    new_image = filter_area(image, coeffs, win_sizes)

    with h5py.File("data/filter_result.hdf", "w") as f:
        f.create_dataset("Before", data=image)
        f.create_dataset("After", data=new_image)


if __name__ == '__main__':
    main()
