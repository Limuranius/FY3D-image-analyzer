import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.ndimage import median_filter
from scipy.signal import convolve
import os
from database import FY3DImage
import numpy as np
from tqdm import tqdm

sns.set_style("darkgrid")
CHANNEL = 8

IMG_ID = 119
IMG = FY3DImage.get(id=IMG_ID)
AREAS = [
    (290, 410, 610),
    # (330, 430, 480),
    # (340, 410, 460),
    # (350, 400, 450),
    # (30, 610, 650),
    # (260, 450, 510)
]

# IMG_ID = 71
# IMG = FY3DImage.get(id=IMG_ID)
# AREAS = [
#     (1420, 400, 460),
#     (1430, 410, 480),
# ]

# IMG_ID = 28
# IMG = FY3DImage.get(id=IMG_ID)
# AREAS = [
#     (630, 750, 810),
#     (640, 760, 820),
#     (610, 770, 830),
#     (620, 800, 850)
# ]


# IMG_ID = 32
# IMG = FY3DImage.get(id=IMG_ID)
# AREAS = [
#     # (570, 459, 499),
#     (580, 450, 510),
# ]


def ch_area_to_df(ch_area: np.ndarray):
    df = pd.DataFrame(columns=["sensor", "x", "value"])
    for sensor in range(10):
        row = ch_area[sensor]
        for x, value in enumerate(row):
            df.loc[len(df)] = [sensor, x, value]
    return df


def ch_area_to_median(ch_area: np.ndarray, kernel=(1, 20)):
    median_area = median_filter(ch_area, size=kernel)
    return median_area


def ch_area_to_sea_mask(ch_area: np.ndarray):
    kernel = np.array([[1, 0, -1]])
    conv_area = convolve(ch_area, kernel, mode="valid")
    threshold_coords = conv_area.argmax(axis=1)
    threshold_coords += 1
    sea_mask = ch_area.copy().astype(np.bool_)
    for sensor, thresh_x in enumerate(threshold_coords):
        sea_mask[sensor, :thresh_x] = True
        sea_mask[sensor, thresh_x:] = False
    return sea_mask


def find_two_peaks(arr: np.ndarray) -> tuple[int, int]:
    hist_y, hist_x = np.histogram(arr, bins=int(arr.max() - arr.min() + 1))
    hist_x = (hist_x[:-1] + hist_x[1:]) / 2

    med = np.median(hist_x)
    left_max_i = hist_y[hist_x <= med].argmax()
    right_max_i = hist_y[hist_x > med].argmax()
    return int(hist_x[left_max_i]), int(hist_x[hist_x > med][right_max_i])


def ch_area_to_deviations(ch_area: np.ndarray):
    median = ch_area_to_median(ch_area)
    sea_mask = ch_area_to_sea_mask(median)
    sea_value, ice_value = find_two_peaks(median)
    res = ch_area.copy().astype(np.int32)
    res[sea_mask] -= sea_value
    res[~sea_mask] -= ice_value
    return res


def f1():
    stats = pd.DataFrame(columns=["sensor", "area_i", "avg_slope"])

    SENSOR = 8
    for SENSOR in range(1, 10):
        print("SENSOR", SENSOR)
        for i, (y, x_min, x_max) in enumerate(AREAS):
            area = IMG.get_area(x=x_min, y=y, w=x_max - x_min, h=10)

            fname = area.get_short_name()
            ch_area = area.get_vis_channel(CHANNEL)

            data = ch_area_to_df(ch_area)
            deviations_df = ch_area_to_df(ch_area_to_deviations(ch_area))
            sea_mask_df = ch_area_to_df(ch_area_to_sea_mask(ch_area_to_median(ch_area)))

            # plt.imshow(ch_area_to_sea_mask(ch_area_to_median(ch_area)))
            # plt.savefig(os.path.join("jopa", "mask " + fname))
            plt.close()

            df = pd.DataFrame(
                {
                    "sensor0": deviations_df[deviations_df.sensor == 0]["value"].tolist(),
                    f"sensor{SENSOR}": data[data.sensor == SENSOR]["value"].tolist(),
                    "is_sea": sea_mask_df[data.sensor == 0]["value"].tolist(),
                }
            )

            s0_dev = df[df["is_sea"] == True]["sensor0"].to_numpy()
            s_values = df[df["is_sea"] == True][f"sensor{SENSOR}"].to_numpy()

            df_diff = pd.DataFrame({
                "sensor0_dev_diff": s0_dev[1:] - s0_dev[:-1],
                f"sensor{SENSOR} diff": s_values[1:] - s_values[:-1]
            })
            slopes = df_diff["sensor0_dev_diff"] / df_diff[f"sensor{SENSOR} diff"]
            slopes = slopes[(slopes != np.inf) & (slopes != -np.inf)]
            # g = sns.relplot(
            #     data=slopes,
            # )
            print("     avg slope: ", slopes.mean())
            stats.loc[len(stats)] = [SENSOR, i, slopes.mean()]
            # plt.savefig(os.path.join("jopa", "slopes " + fname))
            plt.close()

            # g = sns.relplot(
            #     data=df,
            #     x=f"sensor{SENSOR}",
            #     y="sensor0",
            #     hue="is_sea",
            #     kind="line"
            # )
            # g.set(ylim=(-20, 200))
            # plt.savefig(os.path.join("jopa", fname))
            plt.close()
            area.clear_cache()

    sns.relplot(
        data=stats,
        x="area_i",
        y="avg_slope",
        hue="sensor",
        kind="line",
        palette="tab10"
    )
    plt.show()


def f2():
    for i, (y, x_min, x_max) in enumerate(AREAS):
        area = IMG.get_area(x=x_min, y=y, w=x_max - x_min, h=10)
        fname = str(y)
        ch_area = area.get_vis_channel(CHANNEL)
        diff = ch_area[:, 1:].astype(np.int32) - ch_area[:, :-1].astype(np.int32)
        diff = np.insert(diff, 0, 0, axis=1)

        s1 = [*ch_area, [], *diff]

        median = ch_area_to_median(ch_area)

        with pd.ExcelWriter(os.path.join("jopa", fname + ".xlsx")) as writer:
            pd.DataFrame(s1).to_excel(writer, sheet_name=f"Канал {CHANNEL}", index=False)
            pd.DataFrame(median).to_excel(writer, sheet_name=f"Медиана", index=False)
        area.clear_cache()


def show_median():
    for i, (y, x_min, x_max) in enumerate(AREAS):
        area = IMG.get_area(x=x_min, y=y, w=x_max - x_min, h=10)
        ch_area = area.get_vis_channel(CHANNEL)
        median = ch_area_to_median(ch_area, kernel=(1, 80))

        sns.relplot(
            data=ch_area_to_df(median),
            x="x",
            y="value",
            hue="sensor",
            kind="line"
        )
        plt.show()


# f2()
show_median()