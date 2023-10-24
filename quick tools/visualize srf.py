import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

channels = list(range(8, 11))

data = pd.DataFrame(columns=["Wavelength (nm)", "SRF", "channel"])

for channel in channels:
    path = "SRF/FY3D_MERSI_SRF_CH{:02d}_Pub.txt".format(channel)
    with open(path) as f:
        f_data = f.read().split()
        for i in range(0, len(f_data), 2):
            data.loc[len(data)] = [
                float(f_data[i]),
                float(f_data[i+1]),
                channel
            ]

sns.relplot(data=data, x="Wavelength (nm)", y="SRF", kind="line", hue="channel")
plt.show()
