import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
import filter_image
from database import FY3DImage
from utils.some_utils import change_contrast

X = 360
Y = 360
HEIGHT = 50
WIDTH = 90
img = FY3DImage.get(id=119)
ch_img = img.get_vis_channel(12).astype(int)
area = ch_img[Y: Y + HEIGHT, X: X + WIDTH]

fig, ax = plt.subplots()
ax.imshow(area, cmap="gray")

fig.subplots_adjust(left=0.25)

coeffs_sliders = []
init_values = [0.0017875, 0.0019385416666666668, 0.0019463541666666668, 0.0019385416666666668, 0.0020414062500000003, 0.0020440104166666666, 0.0019268229166666667, 0.0018838541666666667, 0.0018473958333333335, 0.0017888020833333334]


for sensor in range(10):
    ax_coeff = fig.add_axes([0.05, 0.1 + 0.07 * sensor, 0.2, 0.05])
    coeff_slider = Slider(
        ax=ax_coeff,
        label=f"Sensor {sensor}",
        valmin=0.0017,
        valmax=0.0021,
        # valmin=0.5,
        # valmax=0.8,
        valinit=init_values[sensor],
    )
    coeffs_sliders.append(coeff_slider)

win_sliders = []
init_values = [12, 12, 14, 16, 16, 16, 17, 16, 14, 13]
for sensor in range(10):
    ax_coeff = fig.add_axes([0.05, 0.087 + 0.07 * sensor, 0.2, 0.03])
    win_slider = Slider(
        ax=ax_coeff,
        label=f"Win {sensor}",
        valmin=1,
        valmax=25,
        valstep=1,
        valinit=init_values[sensor],
    )
    win_sliders.append(win_slider)


# The function to be called anytime a slider's value changes
def update(val):
    coeffs = [slider.val for slider in coeffs_sliders]
    # win_sizes = [18, 20, 20, 20, 21, 21, 21, 19, 19, 17]
    win_sizes = [int(slider.val) for slider in win_sliders]

    # coeffs = [0] * 10

    filtered_area = filter_image.filter_area(area, coeffs, win_sizes)
    # contrast = change_contrast(filtered_area, 300, 600)
    # ax.imshow(contrast, cmap="gray")
    # plt.imshow(area, vmin=300, vmax=600, cmap="gray")
    # plt.savefig("original.jpg", dpi=300)
    #
    # plt.imshow(filtered_area, vmin=300, vmax=600, cmap="gray")
    # plt.savefig("calibrated.jpg", dpi=300)

    # plt.imsave("original.jpg", area, vmin=300, dpi=300, vmax=600, cmap="gray")
    # plt.imsave("calibrated.jpg", filtered_area, dpi=300, vmin=300, vmax=600, cmap="gray")
    ax.imshow(filtered_area, cmap="gray", vmin=300, vmax=600)
    fig.canvas.draw_idle()


for slider in coeffs_sliders:
    slider.on_changed(update)
for slider in win_sliders:
    slider.on_changed(update)
update(1)
plt.show()
print([slider.val for slider in coeffs_sliders])
print([slider.val for slider in win_sliders])
