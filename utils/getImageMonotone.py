from numba import cuda
from FY3DImage import FY3DImage
import numpy as np
import math
import numba
from time import time


@cuda.jit
def calc_std(img, w: int, h: int, out):
    y, x = cuda.grid(2)
    if x + w < 2048 and y + h < 2000 and y % 10 == 0:
        std_sum = 0
        for ch in range(15):
            area_sum = 0
            for i in range(y, y + h):
                for j in range(x, x + w):
                    area_sum += img[ch, i, j]
            area_avg = area_sum / (w * h)
            dev = 0
            for i in range(y, y + h):
                for j in range(x, x + w):
                    dev += (img[ch, i, j] - area_avg) ** 2
            std = math.sqrt(dev / (w * h))
            std_sum += std
        out[y, x] = std_sum


@numba.njit
def calc_std_cpu(img, w: int, h: int, out):
    for x in numba.prange(2048 - w):
        for y in numba.prange(0, 2000 - h, 10):
            std_sum = 0
            for ch in numba.prange(15):
                std_sum += img[ch, y: y + h, x: x + w].std()
            out[y, x] = std_sum


def get_n_min(arr, n: int, win_w: int, win_h: int) -> list[tuple[int, int]]:
    h, w = arr.shape
    arr = arr.flatten()
    order = arr.argsort()
    res = []
    i = 0
    count = 0
    while count != n:
        index = order[i]
        x = index % w
        y = index // w

        # Проверяем, что область не пересекается с другими
        intersect = False
        for area in res:
            if abs(area[0] - x) <= win_w and y == area[1]:
                intersect = True
        if not intersect:
            res.append((x, y))
            count += 1
        i += 1
    return res


def get_min_monotone(image: FY3DImage, count: int) -> list[tuple[int, int]]:
    img = image.EV_1KM_RefSB[:, :, :].astype(np.float64)
    h = 10
    w = 100
    out = np.ones((2000, 2048), dtype=np.float64) * np.inf

    treadsperblock = (16, 16)
    blockspergrid = (128, 128)
    calc_std[blockspergrid, treadsperblock](img, w, h, out)

    # calc_std_cpu(img, w, h, out)

    areas = get_n_min(out, count, w, h)
    for x, y in areas:
        image.add_area(x, y, w, h)
    image.get_colored_picture().save("aboba_all_channels.png")
    return areas


@cuda.jit
def calc_std_for_channel(ch_img, w: int, h: int, out):
    y, x = cuda.grid(2)
    if x + w < 2048 and y + h < 2000 and y % 10 == 0:
        area_sum = 0
        for i in range(y, y + h):
            for j in range(x, x + w):
                area_sum += ch_img[i, j]
        area_avg = area_sum / (w * h)
        dev = 0
        for i in range(y, y + h):
            for j in range(x, x + w):
                dev += (ch_img[i, j] - area_avg) ** 2
        std = math.sqrt(dev / (w * h))
        out[y, x] = std


def get_min_monotone_for_channel(image: FY3DImage, count: int, channel: int) -> list[tuple[int, int]]:
    img = image.EV_1KM_RefSB[channel - 5, :, :].astype(np.float64)
    h = 10
    w = 100
    out = np.ones((2000, 2048), dtype=np.float64) * np.inf

    treadsperblock = (16, 16)
    blockspergrid = (128, 128)
    calc_std_for_channel[blockspergrid, treadsperblock](img, w, h, out)

    # calc_std_cpu(img, w, h, out)

    areas = get_n_min(out, count, w, h)
    for x, y in areas:
        image.add_area(x, y, w, h)
    image.get_colored_picture().save("aboba_one_channel.png")
    return areas


if __name__ == "__main__":
    # img1 = FY3DImage("C:/Users/Gleb/Desktop/Диплом/Снимки со спутников\\17.03.23 06.20 (Берег Австралии)/FY3D_MERSI_GBAL_L1_20230317_0620_1000M_MS.HDF")
    # img2 = FY3DImage("C:/Users/Gleb/Desktop/Диплом/Снимки со спутников\\17.03.23 06.20 (Берег Австралии)/FY3D_MERSI_GBAL_L1_20230317_0620_1000M_MS.HDF")
    # get_min_monotone_for_channel(img1, 10, 8)
    # get_min_monotone(img2, 10)
    #
    # img1.save_to_excel("Монотонен 8 канал.xlsx")
    # img2.save_to_excel("Монотонны все каналы.xlsx")
    img = FY3DImage("C:/Users/Gleb/Desktop/Диплом/Снимки со спутников\\17.03.23 06.20 (Берег Австралии)/FY3D_MERSI_GBAL_L1_20230317_0620_1000M_MS.HDF")
    for y in range(1300, 1631, 10):
        img.add_area(850, y, 100, 10)
    for x in range(850, 1600, 100):
        img.add_area(x, 1300, 100, 10)
    img.save_to_excel("Области в ряд.xlsx")
    img.get_colored_picture().save("Области в ряд.png")



