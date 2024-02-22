import numpy as np
from prepare_results import prepare_results
from database import FY3DImage
import pickle
import extra

A_COEFFS_PATH = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\Результаты\common_coeffs.pkl"
B_COEFFS_PATH = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\Результаты\cal_coeffs.pkl"

IMAGE = FY3DImage.get(id=119)
IMAGE_CHANNEL = IMAGE.get_vis_channel(8)
IMAGE_AREAS = [
    (345, 256, 130, 70, 1000, 1300),
    (400, 275, 130, 70, 1000, 1300),
    (400, 275, 130, 70, 3000, 3500),
    (560, 485, 130, 70, 3400, 3700),
]

AREAS_IDS = [8917, 8918, 8919, 8920]


def get_b_coeffs() -> tuple[np.ndarray, np.ndarray]:
    with open(B_COEFFS_PATH, "rb") as f:
        df = pickle.load(f)

    ch_df = df[df["channel"] == 8]
    b1 = ch_df["slope"].to_numpy()
    b2 = ch_df["intercept"].to_numpy()
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
    name = "Пусто"
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
        image_areas=IMAGE_AREAS
    )


def all_120_at_once():
    """120 коэффициентов оптимизируются одновременно"""
    name = "120 коэффициентов одновременно"
    print(name)

    coeffs_flat = np.zeros(120, dtype=np.float_)
    coeffs_flat[100:110] = 1
    coeffs, func_values_df = extra.optimize_at_once(
        areas=AREAS_IDS,
        n_iters=2,
        flat_coeffs=coeffs_flat
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
        image_areas=IMAGE_AREAS
    )


def a_and_b200():
    """Оптимизируются А и В, но В отдельное для каждого датчика"""
    name = "Оптимизируются А и В, но В отдельное для каждого датчика"

    coeffs = get_empty_coeffs()
    coeffs, func_values_df = extra.optimize_all_sensors(
        areas=AREAS_IDS,
        n_iters=250,
        x0_arr=coeffs
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
        image_areas=IMAGE_AREAS
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
        image_areas=IMAGE_AREAS
    )


def a_fixed_b_optimize():
    """А фиксировано, В подбирается оптимизатором"""
    name = "А фиксировано, В подбирается оптимизатором"

    a_coeffs = get_a_coeffs()
    coeffs, func_values_df = extra.optimize_all_sensors_only_b(
        areas=AREAS_IDS,
        n_iters=250,
        a_coeffs=a_coeffs
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
        image_areas=IMAGE_AREAS
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
        image_areas=IMAGE_AREAS
    )


def a_optimize_b_empty():
    """Оптимизируется только А (У B значения 1 и 0)"""
    name = "Оптимизируется только А (У B значения 1 и 0)"

    a_coeffs = get_a_coeffs()
    b_coeffs = np.array([1] * 10 + [0] * 10)

    coeffs, func_values_df = extra.optimize_only_a(
        areas=AREAS_IDS,
        n_iters=250,
        a_coeffs=a_coeffs,
        b_coeffs=b_coeffs
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
        image_areas=IMAGE_AREAS
    )

def a_optimize_b_regress():
    """Оптимизируется только А (У B значения регрессий)"""
    name = "Оптимизируется только А (У B значения регрессий)"

    a_coeffs = get_a_coeffs()
    b1, b2 = get_b_coeffs()
    b_coeffs = np.array([*b1, *b2])

    coeffs, func_values_df = extra.optimize_only_a(
        areas=AREAS_IDS,
        n_iters=250,
        a_coeffs=a_coeffs,
        b_coeffs=b_coeffs
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
        image_areas=IMAGE_AREAS
    )


METHODS = [
    # empty,
    all_120_at_once,
    a_and_b200,
    a_fixed_b_bruteforce,
    a_fixed_b_optimize,
    a_fixed_b_regress,
    a_optimize_b_empty,
    a_optimize_b_regress,
]

for method in METHODS:
    method()
