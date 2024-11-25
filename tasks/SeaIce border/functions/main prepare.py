import numpy as np
from prepare_results import prepare_results
from database import FY3DImage
import pickle
import extra

A_COEFFS_PATH = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\Результаты\common_coeffs.pkl"
B_COEFFS_PATH = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\Результаты\cal_coeffs.pkl"

CHANNEL = 8

IMAGE = FY3DImage.get(id=119)
IMAGE_CHANNEL = IMAGE.get_vis_channel(CHANNEL)

SEA_VALUES = {
    8: 1000,
    9: 1138,
    10: 900,
    11: 581,
    12: 453,
    13: 444,
    15: 0,
    16: 0,
}

CLOSE_ICE = {
    8: 3000,
    9: 3672,
    10: 4095,
    11: 3362,
    12: 3717,
    13: 3977,
    15: 0,
    16: 0,
}

ICE = {
    8: 1000,
    9: 4095,
    10: 4095,
    11: 3951,
    12: 4095,
    13: 4094,
    15: 0,
    16: 0,
}

BOTTOM_ICE = {
    8: 3200,
    9: 2890,
    10: 3200,
    11: 2435,
    12: 2965,
    13: 3399,
    15: 0,
    16: 0,
}

IMAGE_AREAS = [
    (345, 256, 130, 70, SEA_VALUES[CHANNEL], SEA_VALUES[CHANNEL] + 300),
    (400, 275, 130, 70, SEA_VALUES[CHANNEL], SEA_VALUES[CHANNEL] + 300),
    (400, 275, 130, 70, CLOSE_ICE[CHANNEL], CLOSE_ICE[CHANNEL] + 500),
    (560, 485, 130, 70, ICE[CHANNEL], ICE[CHANNEL] + 400),
    (400, 320, 70, 70, 0, 4096),
    (345, 410, 70, 70, 0, 4096),
    (300, 1640, 200, 200, BOTTOM_ICE[CHANNEL], BOTTOM_ICE[CHANNEL] + 500),
]

AREAS_IDS = [8917, 8918, 8919, 8920]


# AREAS_IDS = [8917, 8918, 8919, 8920] + [8921, 8922, 8923, 8924, 8925, 8926, 8927, 8928, 8929]

def get_b_coeffs() -> tuple[np.ndarray, np.ndarray]:
    with open(B_COEFFS_PATH, "rb") as f:
        df = pickle.load(f)
    ch_df = df[df["channel"] == CHANNEL]
    b1 = ch_df["slope"].to_numpy()
    b1 = -b1
    b1 += 1
    b2 = ch_df["intercept"].to_numpy()
    b2 = -b2
    return b1, b2


def get_a_coeffs():
    with open(A_COEFFS_PATH, "rb") as f:
        a = pickle.load(f)
        return a


def get_empty_coeffs() -> np.ndarray:
    x0 = np.zeros((10, 30))
    x0[:, 10:20] = 1
    return x0


def set_a(coeffs: np.ndarray) -> np.ndarray:
    a = get_a_coeffs()
    coeffs[:, 0: 10] = a
    return coeffs


def set_b(coeffs: np.ndarray) -> np.ndarray:
    b1, b2 = get_b_coeffs()
    coeffs[:, 10:20] = b1
    coeffs[:, 20:30] = b2
    return coeffs


def split_coeffs(coeffs: np.ndarray, unique_b: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    a = coeffs[:, 0:10]
    if unique_b:
        b1 = coeffs[0, 10:20]
        b2 = coeffs[0, 20:30]
    else:
        b1 = coeffs[:, 10:20]
        b2 = coeffs[:, 20:30]
    return a, b1, b2


def empty():
    name = "Без обработки"
    coeffs = get_empty_coeffs()
    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=None,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def all_120_at_once():
    """120 коэффициентов оптимизируются одновременно"""
    name = "120 коэффициентов одновременно"

    coeffs_flat = np.zeros(120, dtype=np.float_)
    coeffs_flat[100:110] = 1
    coeffs, func_values_df = extra.optimize_at_once(
        area_ids=AREAS_IDS,
        n_iters=2,
        flat_coeffs=coeffs_flat,
        channel=CHANNEL
    )

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)

    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=func_values_df,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def a_and_b200():
    """Оптимизируются А и В, но В отдельное для каждого датчика"""
    name = "Оптимизируются А и В, но В отдельное для каждого датчика"

    coeffs = get_empty_coeffs()
    coeffs, func_values_df = extra.optimize_all_sensors(
        area_ids=AREAS_IDS,
        n_iters=30,
        start_coeffs=coeffs,
        channel=CHANNEL,
    )

    a, b1, b2 = split_coeffs(coeffs, unique_b=False)

    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=func_values_df,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def a_fixed_b_bruteforce():
    """A фиксировано, В подбираются поочерёдным перебором"""
    name = "A фиксировано, В подбираются поочерёдным перебором"

    coeffs = get_empty_coeffs()
    set_a(coeffs)
    coeffs, func_values_df = extra.bruteforce_b(
        areas=AREAS_IDS,
        coeffs=coeffs
    )

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=func_values_df,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def a_fixed_b_optimize():
    """А фиксировано, В подбирается оптимизатором"""
    name = "А фиксировано, В подбирается оптимизатором"

    a_coeffs = get_a_coeffs()
    coeffs, func_values_df = extra.optimize_all_sensors_only_b(
        area_ids=AREAS_IDS,
        n_iters=250,
        a_coeffs=a_coeffs,
        channel=CHANNEL,
    )

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=func_values_df,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def a_fixed_b_regress():
    """А фиксировано, В фиксировано (задано регрессиями)"""
    name = "А фиксировано, В фиксировано (задано регрессиями)"

    coeffs = get_empty_coeffs()
    set_a(coeffs)
    set_b(coeffs)

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=None,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def a_optimize_b_empty():
    """Оптимизируется только А (У B значения 1 и 0)"""
    name = "Оптимизируется только А (У B значения 1 и 0)"

    a_coeffs = get_a_coeffs()
    b_coeffs = np.array([1] * 10 + [0] * 10)

    coeffs, func_values_df = extra.optimize_only_a(
        area_ids=AREAS_IDS,
        n_iters=30,
        a_coeffs=a_coeffs,
        b_coeffs=b_coeffs,
        channel=CHANNEL,
    )

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=func_values_df,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def a_optimize_b_regress():
    """Оптимизируется только А (У B значения регрессий)"""
    name = "Оптимизируется только А (У B значения регрессий)"

    # a_coeffs = get_a_coeffs()
    a_coeffs = np.zeros((10, 10))

    b1, b2 = get_b_coeffs()
    b_coeffs = np.array([*b1, *b2])

    coeffs, func_values_df = extra.optimize_only_a(
        area_ids=AREAS_IDS,
        n_iters=30,
        a_coeffs=a_coeffs,
        b_coeffs=b_coeffs,
        channel=CHANNEL,
    )

    # coeffs[1:, 0:10] = 0

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=func_values_df,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL,
        save_image=True
    )


def a_empty_b_regress():
    """Используются только коэффициенты b"""
    name = "Используются только коэффициенты b"

    coeffs = get_empty_coeffs()
    set_b(coeffs)

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=None,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL
    )


def hardcoded():
    """Хардкод коэффициентов"""
    name = "Хардкод коэффициентов"

    coeffs = get_empty_coeffs()
    set_b(coeffs)

    coeffs[0, 0:10] = [0.0, -0.325904942182169, 0.039503873453768414, 0.002178551017844806, 0.0, 0.0, 0.0, 0.0, 0.0,
                       0.0]
    coeffs[1, 0:10] = [0.04528322660535034, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    coeffs[2, 0:10] = [0.0, 0.019657839757946396, 0.0, 0.10128825399717674, -0.034506795813790715, 0.0, 0.0, 0.0, 0.0,
                       0.0]
    coeffs[3, 0:10] = [0.0, 0.0, -0.032604940002037563, 0.0, -0.06748467434671863, 0.010293292383290766, 0.0, 0.0, 0.0,
                       0.0]
    coeffs[4, 0:10] = [0.0, 0.0, 0.0, -0.004045743899488774, 0.0, -0.003849175102416108, 0.0011520137524973248, 0.0,
                       0.0, 0.0]
    coeffs[5, 0:10] = [0.0, 0.0, 0.0, 0.0, -0.0060672298199046385, 0.0, -0.001376465934001201, -0.0018096297933889074,
                       0.0, 0.0]
    coeffs[6, 0:10] = [0.0, 0.0, 0.0, 0.0, 0.0, -0.007081708923597449, 0.0, -0.005445760533543948, 0.004441628876658325,
                       -0.003240235124044002]
    coeffs[7, 0:10] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.003931848605560104, 0.0, 0.0035129064160984596,
                       -0.0051559194865284045]
    coeffs[8, 0:10] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.017139876093015302, -0.09456106030177251, 0.07629128932556489, 0.0,
                       0.06856055001882054]
    coeffs[9, 0:10] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.049154477210051624, 0.1281246119097821, -0.5095479757152046,
                       0.0]

    coeffs[0, 0:10] = -coeffs[0, 0:10]
    coeffs[1, 0:10] = -coeffs[1, 0:10]
    coeffs[2, 0:10] = -coeffs[2, 0:10]
    coeffs[3, 0:10] = -coeffs[3, 0:10]
    coeffs[4, 0:10] = -coeffs[4, 0:10]
    coeffs[5, 0:10] = -coeffs[5, 0:10]
    coeffs[6, 0:10] = -coeffs[6, 0:10]
    coeffs[7, 0:10] = -coeffs[7, 0:10]
    coeffs[8, 0:10] = -coeffs[8, 0:10]
    coeffs[9, 0:10] = -coeffs[9, 0:10]

    a, b1, b2 = split_coeffs(coeffs, unique_b=True)
    prepare_results(
        name=name,
        a_coeffs=a,
        b1_coeffs=b1,
        b2_coeffs=b2,
        areas_ids=AREAS_IDS,
        func_values_df=None,
        image=IMAGE_CHANNEL,
        image_areas=IMAGE_AREAS,
        channel=CHANNEL,
        save_image=True
    )


METHODS = [
    empty,
    # all_120_at_once,
    # a_and_b200,
    # a_fixed_b_bruteforce,
    # a_fixed_b_optimize,
    # a_fixed_b_regress,

    # a_optimize_b_empty,
    # a_optimize_b_regress,

    # a_empty_b_regress,
    # hardcoded,
]

for method in METHODS:
    method()
