import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.area_utils import ch_area_rows_deviations
from database import FY3DImageArea
from tqdm import tqdm
import seaborn as sns

sns.set_style("darkgrid")


def load_coeffs():
    with open("coeffs2023.pkl", "rb") as f:
        coeffs_df = pickle.load(f)

    def get_coeffs(channel: int, sensor: int) -> tuple[float, float]:
        coeff = coeffs_df[(coeffs_df["channel"] == channel) & (coeffs_df["sensor"] == sensor)].squeeze()
        slope = coeff["slope"]
        intercept = coeff["intercept"]
        return slope, intercept

    slopes = dict()
    intercepts = dict()
    for channel in range(8, 20):
        ch_slopes = []
        ch_intercepts = []
        for sensor in range(10):
            slope, intercept = get_coeffs(channel, sensor)
            ch_slopes.append(slope)
            ch_intercepts.append(intercept)
        slopes[channel] = np.array(ch_slopes)
        intercepts[channel] = np.array(ch_intercepts)
    return slopes, intercepts


SLOPES, INTERCEPTS = load_coeffs()


def areas_to_deviations(areas: list[np.ndarray]) -> pd.DataFrame:
    df = pd.DataFrame(
        columns=["sensor", "deviation", "area_avg"],
        index=range(len(areas) * 10))
    i = 0
    for area in tqdm(areas):
        area_avg = area.mean()
        deviations = ch_area_rows_deviations(area)
        for sensor in range(10):
            df.loc[i] = [sensor, deviations[sensor], area_avg]
            i += 1
    df = df[df.deviation.abs() < 40]
    return df


def fix_areas(areas: list[np.ndarray], channel: int):
    new_areas = []
    for area in tqdm(areas, desc=f"Fixing channel {channel}"):
        slope = SLOPES[channel].reshape((10, 1))
        intercept = INTERCEPTS[channel].reshape((10, 1))
        # deviations = area * slope + intercept
        new_area = area - area * slope + intercept
        new_areas.append(new_area)
    return new_areas


def deviations_to_sensor_stats(deviations_df: pd.DataFrame) -> list[tuple[float, float]]:
    """
    return 10 * (std, avg)

    df:
        sensor
        deviation
    """
    result = []
    for sensor in range(10):
        sensor_df = deviations_df[deviations_df.sensor == sensor]
        std = sensor_df.deviation.std()
        avg = sensor_df.deviation.mean()
        result.append((std, avg))
    return result


def channels_stats_to_excel(filename, channels_stats) -> None:
    writer = pd.ExcelWriter(filename)

    pretty_data_std = []
    pretty_data_std.append([""] + list(range(10)))
    for channel, stats in channels_stats:
        channel_row = [f"Канал {channel}"]
        for sensor, (std, _) in enumerate(stats):
            channel_row.append(std)
        pretty_data_std.append(channel_row)
    df = pd.DataFrame(pretty_data_std)
    df.to_excel(writer, sheet_name="std", index=False, header=False)

    pretty_data_avg = []
    pretty_data_avg.append([""] + list(range(10)))
    for channel, stats in channels_stats:
        channel_row = [f"Канал {channel}"]
        for sensor, (_, avg) in enumerate(stats):
            channel_row.append(avg)
        pretty_data_avg.append(channel_row)
    df = pd.DataFrame(pretty_data_avg)
    df.to_excel(writer, sheet_name="avg", index=False, header=False)

    writer.close()


def get_channels_stats(areas: list[FY3DImageArea], do_fix: bool):
    channels_stats = []
    for channel in range(8, 20):
        ch_areas = []
        for area in tqdm(areas):
            ch_areas.append(area.get_vis_channel(channel))

        if do_fix:
            ch_areas = fix_areas(ch_areas, channel)

        devs = areas_to_deviations(ch_areas)
        stats = deviations_to_sensor_stats(devs)
        channels_stats.append((channel, stats))
    return channels_stats


def main():
    areas = FY3DImageArea.find(year=2023)

    channels_stats_to_excel("before.xlsx", get_channels_stats(areas, do_fix=False))
    channels_stats_to_excel("after.xlsx", get_channels_stats(areas, do_fix=True))


def show():
    CHANNEL = 8
    areas = FY3DImageArea.find(year=2023)

    ch_areas = []
    for area in tqdm(areas):
        ch_areas.append(area.get_vis_channel(CHANNEL))
    ch_areas = fix_areas(ch_areas, CHANNEL)
    df = areas_to_deviations(ch_areas)

    sns.relplot(
        data=df,
        x="area_avg",
        y="deviation",
        kind="scatter",
        row="sensor"
    )
    plt.savefig("after.jpg", dpi=300)


main()
show()
