import numpy as np
from database import ChannelArea
from vars import SurfaceType
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import filter_image

sns.set_style("darkgrid")

CHANNEL = 8


def preprocess_area(
        channel_area: ChannelArea,
        coeffs: np.ndarray
) -> np.ndarray:
    arr = channel_area.to_numpy()
    arr = filter_image.filter_area(arr, coeffs)
    bb = channel_area.parent.get_black_body_value(8)
    arr = arr - bb

    return arr


def collect_data(coeffs: np.ndarray) -> pd.DataFrame:
    sea_areas = ChannelArea.find(
        channel=CHANNEL,
        surface_type=SurfaceType.SEA,
        year=2023
    )

    ice_areas = ChannelArea.find(
        channel=CHANNEL,
        surface_type=SurfaceType.SNOW,
        year=2023
    )

    print(len(sea_areas))
    print(len(ice_areas))

    count = len(sea_areas) * 100 + len(ice_areas) * 100

    df = pd.DataFrame(
        columns=["main_sensor", "other_sensor", "relation", "surface_type"],
        index=range(count)
    )

    i = 0
    for area in tqdm(sea_areas):
        arr = preprocess_area(area, coeffs)
        for main_sensor in range(10):
            for other_sensor in range(10):
                relation = arr[main_sensor].sum() / arr[other_sensor].sum()
                df.loc[i] = [main_sensor, other_sensor, relation, "SEA"]
                i += 1

    for area in tqdm(ice_areas):
        arr = preprocess_area(area, coeffs)
        for main_sensor in range(10):
            for other_sensor in range(10):
                relation = arr[main_sensor].sum() / arr[other_sensor].sum()
                df.loc[i] = [main_sensor, other_sensor, relation, "ICE"]
                i += 1

    df = df[df["main_sensor"] != df["other_sensor"]]

    return df


# print(df.groupby(["main_sensor", "other_sensor", "surface_type"]).agg(["mean", "std"]))
# df.groupby(["main_sensor", "other_sensor", "surface_type"]).agg(["mean", "std"]).to_excel("aboba.xlsx")



