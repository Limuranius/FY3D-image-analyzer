import numpy as np
from database import FY3DImage
import cv2
from utils.some_utils import change_contrast

img: FY3DImage = FY3DImage.get(id=119)

colored = np.array(img.get_colored_picture(draw_areas=False))
cv2.imwrite("colored.jpg", cv2.cvtColor(colored, cv2.COLOR_RGB2BGR))

ch8 = img.get_vis_channel(8)
ch8_ice_contrast = change_contrast(ch8, 3300, 3700)

# Сжимаем 12 бит до 8 бит
ch8 = np.uint8(ch8 // 16)
ch8_ice_contrast = np.uint8(ch8_ice_contrast // 16)

cv2.imwrite("ch8.jpg", ch8)
cv2.imwrite("ch8_ice_contrast.jpg", ch8_ice_contrast)


ch12 = img.get_vis_channel(12)
ch12_contrast = change_contrast(ch12, 400, 900)

# Сжимаем 12 бит до 8 бит
ch12_contrast = np.uint8(ch12_contrast // 16)

cv2.imwrite("ch12_contrast.jpg", ch12_contrast)
