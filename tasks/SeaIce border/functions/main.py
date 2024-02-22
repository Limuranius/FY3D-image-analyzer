import pickle
import numpy as np
import extra
import visual
import timeresults

np.set_printoptions(suppress=True)

A_COEFFS_PATH = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\Результаты\common_coeffs.pkl"
FUNC_VALUES_PATH = timeresults.get_session_path("func_values.pkl")
OUTPUT_COEFFS_PATH = timeresults.get_session_path("coeffs.pkl")

"""
coeffs:
0-9 - a
10-19 - b1
20-29 - b2
"""


def x0_empty() -> np.ndarray:
    x0 = np.zeros((10, 30))
    x0[:, 10:20] = 1
    return x0


def x0_a_set():
    a = get_a_coeffs()
    x0 = x0_empty()
    x0[:, 0: 10] = a
    return x0


def get_a_coeffs():
    with open(A_COEFFS_PATH, "rb") as f:
        a = pickle.load(f)
        return a


def only_b():
    a = get_a_coeffs()
    ids = [8917, 8918, 8919, 8920]
    coeffs, func_values = extra.optimize_all_sensors_only_b(
        areas=ids,
        n_iters=100,
        a_coeffs=a
    )
    visual.func_values(func_values)
    with open(FUNC_VALUES_PATH, "wb") as f:
        pickle.dump(func_values, f)
    with open(OUTPUT_COEFFS_PATH, "wb") as f:
        pickle.dump(coeffs, f)


def main():
    x0 = x0_a_set()
    # x0 = x0_empty()

    ids = [8917, 8918, 8919, 8920]

    coeffs, func_values = extra.optimize_all_sensors(
        areas=ids,
        n_iters=10,
        x0_arr=x0,
    )

    visual.func_values(func_values)

    with open(FUNC_VALUES_PATH, "wb") as f:
        pickle.dump(func_values, f)

    with open(OUTPUT_COEFFS_PATH, "wb") as f:
        pickle.dump(coeffs, f)


def show_sensors():
    ids = [8917, 8918, 8919, 8920]
    with open(OUTPUT_COEFFS_PATH, "rb") as f:
        coeffs = pickle.load(f)
    visual.visualize_all(coeffs, ids)


def show_sensors_before():
    ids = [8917, 8918, 8919, 8920]
    coeffs = x0_a_set()
    visual.visualize_all(coeffs, ids)


main()
# only_b()
show_sensors()
# show_sensors_before()
