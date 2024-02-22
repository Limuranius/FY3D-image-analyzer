from database import ChannelArea
from vars import SurfaceType
import pandas as pd
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import os

sns.set_style("darkgrid")


if not os.path.exists("aboba.pkl"):
    sea_areas = ChannelArea.find(
        channel=8,
        surface_type=SurfaceType.SEA,
        year=2023
    )

    ice_areas = ChannelArea.find(
        channel=8,
        surface_type=SurfaceType.SNOW,
        year=2023
    )

    print(len(sea_areas))
    print(len(ice_areas))

    COUNT = len(sea_areas) * 100 + len(ice_areas) * 100

    df = pd.DataFrame(
        columns=["main_sensor", "other_sensor", "relation", "surface_type"],
        index=range(COUNT)
    )

    i = 0
    for area in tqdm(sea_areas):
        arr = area.to_numpy() - area.parent.get_black_body_value(8)
        for main_sensor in range(10):
            for other_sensor in range(10):
                relation = arr[main_sensor].sum() / arr[other_sensor].sum()
                df.loc[i] = [main_sensor, other_sensor, relation, "SEA"]
                i += 1

    for area in tqdm(ice_areas):
        arr = area.to_numpy() - area.parent.get_black_body_value(8)
        for main_sensor in range(10):
            for other_sensor in range(10):
                relation = arr[main_sensor].sum() / arr[other_sensor].sum()
                df.loc[i] = [main_sensor, other_sensor, relation, "ICE"]
                i += 1
    df.to_pickle("aboba.pkl")
else:
    df = pd.read_pickle("aboba.pkl")

print(df.groupby(["main_sensor", "other_sensor", "surface_type"]).agg(["mean", "std"]))
df.groupby(["main_sensor", "other_sensor", "surface_type"]).agg(["mean", "std"]).to_excel("aboba.xlsx")

df = df[df["main_sensor"] != df["other_sensor"]]
sns.displot(
    data=df,
    x="relation",
    row="main_sensor",
    col="other_sensor",
    hue="surface_type"
)
plt.savefig("aboba.png", dpi=300)
