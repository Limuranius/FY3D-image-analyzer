from database import FY3DImage
import matplotlib.pyplot as plt
from utils.some_utils import change_contrast


img = FY3DImage.get(id=119)
ch_img = img.get_vis_channel(8)
ch_img = change_contrast(ch_img, 1000, 1300)

plt.imshow(ch_img, cmap="grey")
plt.show()
