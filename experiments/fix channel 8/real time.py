import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
import ch8_utils
from database import FY3DImage
from utils.some_utils import change_contrast

X = 400
Y = 240
HEIGHT = 100
WIDTH = 120

# X = 300
# Y = 240
# HEIGHT = 300
# WIDTH = 220

# 8
MIN_VALUE = 1000
MAX_VALUE = 1300
CHANNEL = 8

# 10
# MIN_VALUE = 500
# MAX_VALUE = 900
# CHANNEL = 10

img = FY3DImage.get(id=119)
ch_img = img.get_vis_channel(CHANNEL).astype(int)
area = ch_img[Y: Y + HEIGHT, X: X + WIDTH]

fig, ax = plt.subplots()
ax.imshow(area, cmap="gray")

fig.subplots_adjust(left=0.25)

# Make a vertically oriented slider to control the amplitude
coeffs_sliders = []
for sensor in range(10):
    ax_coeff = fig.add_axes([0.05, 0.1 + 0.07 * sensor, 0.2, 0.05])
    coeff_slider = Slider(
        ax=ax_coeff,
        label=f"Sensor {sensor}",
        valmin=0,
        valmax=0.1,
        valinit=0,
        # orientation="vertical"
    )
    coeffs_sliders.append(coeff_slider)


# The function to be called anytime a slider's value changes
def update(val):
    coeffs = np.array([slider.val for slider in coeffs_sliders])

    filtered_area = ch8_utils.filter_area(area, coeffs)
    ax.imshow(filtered_area, cmap="gray", vmin=MIN_VALUE, vmax=MAX_VALUE)
    fig.canvas.draw_idle()


for slider in coeffs_sliders:
    slider.on_changed(update)
update(1)
plt.show()
