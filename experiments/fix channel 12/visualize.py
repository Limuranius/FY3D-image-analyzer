import numpy as np

from database import FY3DImage
import matplotlib.pyplot as plt
import pandas as pd

Y = 410
X = 390
WIDTH = 40
img = FY3DImage.get(id=119)
ch_img = img.get_vis_channel(12).astype(int)
area = ch_img[Y: Y + 10, X: X + WIDTH]

# pd.DataFrame(area).to_excel("area.xlsx", index=False)

# sensor = area[5]
# diff = sensor[1:] - sensor[:-1]

# plt.plot(diff)
# plt.grid()
plt.imshow(area, cmap="gray")
plt.show()

def find_mean_water_brightness(area: np.ndarray) -> float:
    hist_y, hist_x = np.histogram(area[area < 2000], bins=50)
    return float((hist_x[hist_y.argmax()] + hist_x[hist_y.argmax() + 1]) / 2)
print(find_mean_water_brightness(area))

plt.hist(area.flatten(), bins=50)
plt.show()
