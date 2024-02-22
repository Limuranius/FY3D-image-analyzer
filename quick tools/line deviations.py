from database import Deviations
import matplotlib.pyplot as plt
from vars import KMirrorSide, SurfaceType
import seaborn as sns
import pandas as pd
from tqdm import tqdm
from database import FY3DImage

id = 119
y_min = 260
chunk_width = 5
channel = 8

img = FY3DImage.get(id=id)
data = pd.DataFrame(columns=["x", "channel", "sensor", "deviation"], index=range(15 * 10 * (2048 // chunk_width)))
area = img.get_area(x=0, y=y_min, h=10, w=2048)
i = 0
# sensors = list(range(10))
sensors = [0, 9]

with tqdm(total=15 * 10 * (2048 // chunk_width)) as pbar:
    for channel in range(5, 20):
        ch_area = area.get_vis_channel(channel)
        for x in range(0, 2048, chunk_width):
            chunk = ch_area[:, x: x + chunk_width]
            chunk_avg = chunk.mean()
            for sensor in sensors:
                sensor_avg = chunk[sensor].mean()
                deviation = sensor_avg - chunk_avg
                data.loc[i] = [x, channel, sensor, deviation]
                i += 1
                pbar.update(1)

sns.relplot(data=data[data.channel == channel], x="x", y="deviation", hue="sensor", kind="line", height=6, aspect=2,
            palette="tab10")
plt.show()
