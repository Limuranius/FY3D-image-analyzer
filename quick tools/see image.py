import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
from database import FY3DImage

CHANNEL = 11

img = FY3DImage.get(id=119)
ch_img = img.get_vis_channel(CHANNEL).astype(int)

fig, ax = plt.subplots()
ax.imshow(ch_img, cmap="gray")

fig.subplots_adjust(left=0.25)

ax1 = fig.add_axes([0.05, 0.2, 0.2, 0.05])
slider1 = Slider(
    ax=ax1,
    label="Min",
    valmin=0,
    valmax=4000,
    valinit=0,
    valstep=1,
)

ax2 = fig.add_axes([0.05, 0.1, 0.2, 0.05])
slider2 = Slider(
    ax=ax2,
    label="Max",
    valmin=0,
    valmax=4000,
    valinit=4000,
    valstep=1,
)

def update(val):
    min_value = slider1.val
    max_value = slider2.val

    ax.imshow(ch_img, cmap="gray", vmin=min_value, vmax=max_value)
    fig.canvas.draw_idle()

slider1.on_changed(update)
slider2.on_changed(update)

update(1)
plt.show()
