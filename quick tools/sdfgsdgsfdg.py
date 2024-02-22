import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from database import FY3DImage

sns.set_style("darkgrid")
IMG_ID = 119
CHANNEL = 8
SENSORS = list(range(10))


y = 290
x_min = 465
x_max = 505

img = FY3DImage.get(id=IMG_ID)
area = img.get_area(x=x_min, y=y, w=x_max - x_min, h=10)
ch_area = area.get_vis_channel(CHANNEL)
df = pd.DataFrame(columns=["sensor", "x", "value", "col_avg"])
for sensor in SENSORS:
    row = ch_area[sensor]
    for i, value in enumerate(row):
        x = x_min + i
        col_avg = ch_area[:, i].mean()
        df.loc[len(df)] = [sensor, x, value, col_avg]


def sensors_values():
    g = sns.relplot(data=df, x="x", y="value", hue="sensor", kind="line", palette="tab10")
    # g.set(ylim=(1000, 1200))
    plt.show()


def sensor0_mean_relation():
    s0_df = df[df.sensor == 0]
    s0_df.loc[:, "value"] /= s0_df["col_avg"]
    # plt.plot(s0_df.x, s0_df.value)
    # plt.plot(s0_df.x, s0_df.col_avg)
    # sns.relplot(data=s0_df, x="col_avg", y="value", kind="line")
    sns.relplot(data=s0_df, x="x", y="value", kind="line")
    plt.show()


def f1():
    s0_df = df[df.sensor == 0]
    s0_df.loc[:, "value"] -= df[df.sensor == 1].value.set_axis(s0_df.index)
    g = sns.relplot(data=s0_df, x="x", y="value")
    g.set(ylim=(-50, 50))
    plt.show()


def f2():
    s0_df = df[df.sensor == 0]
    s1_df = df[df.sensor == 1]
    data = pd.DataFrame()
    data["s0_value"] = s0_df.value
    data["s1_value"] = s1_df.value.set_axis(data.index)

    g = sns.relplot(data=data, x="s1_value", y="s0_value", kind="line")
    plt.show()


# sensor0_mean_relation()
sensors_values()
# f2()
