import matplotlib.pyplot as plt
from database import FY3DImageArea
import pandas as pd

# ID = 8934  # vertical
ID = 8917  # skewed
CHANNEL = 12
SENSORS = list(range(10))

area: FY3DImageArea = FY3DImageArea.get(id=ID)
ch_area = area.get_vis_channel(CHANNEL)
x = list(range(ch_area.shape[1]))
for sensor in SENSORS:
    plt.plot(x, ch_area[sensor], label=sensor)

plt.xlabel("Номер столбца пикселей")
plt.ylabel("Яркость")
# plt.grid()
plt.legend(title="Номер датчика")
plt.title("Яркость пикселей датчиков")
plt.show()
