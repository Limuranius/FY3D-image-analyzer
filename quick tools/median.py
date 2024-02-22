import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from database import FY3DImage

sns.set_style("darkgrid")
IMG_ID = 119
CHANNEL = 8
# sensors = [0, 1, 5, 9]
sensors = list(range(10))

y = 290
x_min = 410
x_max = 590
WINDOW_W = 31

img = FY3DImage.get(id=IMG_ID)
area = img.get_area(x=x_min, y=y, w=x_max - x_min, h=10)
ch_area = area.get_vis_channel(CHANNEL)
df = pd.DataFrame(columns=["sensor", "x", "median"])
for sensor in sensors:
    row = ch_area[sensor]
    width = row.shape[0]
    for i in range(width - WINDOW_W):
        x = x_min + i
        window = row[i: i + WINDOW_W]
        median = np.median(window)
        df.loc[len(df)] = [sensor, x, median]


# sns.relplot(
#     data=df,
#     x="x",
#     y="median",
#     hue="sensor",
#     kind="line",
#     palette="tab10"
# )
sns.histplot(
    data=df,
    x="median",
    bins=len(df["median"].unique())
)
plt.show()
