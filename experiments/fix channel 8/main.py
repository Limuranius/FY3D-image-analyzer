from matplotlib import pyplot as plt
import ch8_utils
from database import FY3DImageArea, FY3DImage

area = FY3DImageArea.get(id=8917).get_vis_channel(8).astype(int)

true = ch8_utils.get_true_sea_values(area)

noise = area - true

# plt.imshow(area, cmap="gray")
plt.plot(noise[0])

plt.show()
