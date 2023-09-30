import numpy as np
from tqdm import tqdm
from time import time
import pyopencl as cl


def calc_area_sum_std(img, w: int, h: int, out, x_min, x_max, y_min, y_max):
    for x in range(x_min, min(x_max, 2048 - w)):
        for y in range(y_min, min(y_max, 2000 - h), 10):
            std_sum = 0
            for ch in range(15):
                std_sum += img[ch, y: y + h, x: x + w].std()
            out[y, x] = std_sum


def get_n_min(std_sum_map, n: int, win_w: int, win_h: int, max_std: int) -> list[tuple[int, int]]:
    h, w = std_sum_map.shape
    std_sum_map = std_sum_map.flatten()
    order = std_sum_map.argsort()
    res = []
    i = 0
    count = 0

    while count != n:
        index = order[i]
        x = index % w
        y = index // w

        if std_sum_map[index] > max_std:
            break

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


def calc_std_sum_map(img: np.ndarray):
    out = np.ones((2000, 2048), dtype=np.float16) * np.inf
    img = img[:].astype(np.uint16)
    w = 2048 - 100
    h = 2000 - 10

    with tqdm(total=w * (h // 10), desc="Std sum map: ") as pbar:
        for x in range(0, w):
            for y in range(0, h, 10):
                area = img[:, y: y + 10, x: x + 100]
                std_sum = np.std(area, (1, 2)).sum()
                out[y, x] = std_sum
                pbar.update(1)
    return out


def calc_std_sum_map_gpu(img: np.ndarray):
    # img: [15, 2000, 2048]
    img = img[:]
    flat_img = img.flatten().astype(np.uint16)

    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

    mf = cl.mem_flags
    flat_g = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=flat_img)

    res_np = np.ones(2000 * 2048, dtype=np.float32) * np.inf
    res_g = cl.Buffer(ctx, mf.WRITE_ONLY | mf.COPY_HOST_PTR, hostbuf=res_np)

    prg = cl.Program(ctx, """
    __kernel void std_sum_map(
        __global const ushort *img_g, __global float *res_g)
    {
        int gid = get_global_id(0);
        int y = gid / 2048;
        int x = gid % 2048;
        if (y < 2000 - 10 && x < 2048 - 100 && y % 10 == 0) {
            float std_sum = 0;

            for (int ch = 0; ch < 15; ch++) {
                int area_sum = 0;
                for (int i = y; i < y + 10; i++) {
                    for (int j = x; j < x + 100; j++) {
                        int index = ch * (2000 * 2048) + i * (2048) + j;
                        area_sum += img_g[index];
                    }
                }
                float area_avg = (float)area_sum / (100.0 * 10.0);
                float dev = 0;
                for (int i = y; i < y + 10; i++) {
                    for (int j = x; j < x + 100; j++) {
                        int index = ch * (2000 * 2048) + i * (2048) + j;
                        dev += (img_g[index] - area_avg) * (img_g[index] - area_avg);
                    }
                }
                float std = sqrt(dev / (100.0 * 10.0));
                std_sum += std;
            }
            res_g[gid] = std_sum;
        }
    }
    """).build()

    knl = prg.std_sum_map  # Use this Kernel object for repeated calls
    knl(queue, (2000 * 2048,), None, flat_g, res_g)

    cl.enqueue_copy(queue, res_np, res_g)
    return res_np.reshape((2000, 2048))


def compress_std_sum_map(std_map: np.ndarray):
    compressed = std_map[0:2000:10]
    return compressed


def uncompress_std_sum_map(comp_std_map: np.ndarray):
    uncompressed = np.ones((2000, 2048), dtype=np.float16) * np.inf
    for i in range(comp_std_map.shape[0]):
        uncompressed[i * 10] = comp_std_map[i]
    return uncompressed


def get_monotone_areas(comp_std_map: np.ndarray, count=30,
                       x_min=0, x_max=2048, y_min=0, y_max=2000, max_std=200) -> list[tuple[int, int]]:
    std_sum_map = uncompress_std_sum_map(comp_std_map)
    std_sum_map[:, :x_min] = np.inf
    std_sum_map[:, x_max:] = np.inf
    std_sum_map[:y_min, :] = np.inf
    std_sum_map[y_max:, :] = np.inf
    areas = get_n_min(std_sum_map, count, 100, 10, max_std)
    return areas
