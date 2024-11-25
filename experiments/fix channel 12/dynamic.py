import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
from database import FY3DImage, FY3DImageArea
import ch12_utils

Y = 410
X = 390
WIDTH = 45
SENSOR = 5
img = FY3DImage.get(id=119)
ch_img = img.get_vis_channel(12).astype(int)
area = ch_img[Y: Y + 10, X: X + WIDTH]

true = ch12_utils.get_true_sea_values(area)
target = (area - ch12_utils.get_true_sea_values(area))


def get_data() -> tuple[np.ndarray, np.ndarray]:
    # returns area and target noise

    # areas_ids = [8934, 8935, 8936, 8937, 8938]
    areas_ids = [8934]
    areas = [FY3DImageArea.get(id=area_id).get_vis_channel(12).astype(int) for area_id in areas_ids]
    targets = [area - ch12_utils.get_true_sea_values(area) for area in areas]
    return (
        np.concatenate(areas, axis=1),
        np.concatenate(targets, axis=1)
    )


area, target = get_data()

# Create the figure and the line that we will manipulate
fig, ax = plt.subplots()
ax.set_xlabel("x")
ax.set_ylabel("Остаточный сигнал")
ax.grid()

ax.plot(target[SENSOR])
line = ax.plot(ch12_utils.predict_noise(area[SENSOR], 0, 1))[0]

# adjust the main plot to make room for the sliders
fig.subplots_adjust(bottom=0.25)

# Make a horizontal slider to control the frequency.
ax_coeff = fig.add_axes([0.25, 0.1, 0.65, 0.03])
coeff_slider = Slider(
    ax=ax_coeff,
    label='Coeff',
    valmin=0,
    # valmax=0.2,
    # valmax=0.01,
    valmax=3,
    valinit=0,
)

ax_win_size = fig.add_axes([0.25, 0.15, 0.65, 0.03])
win_size_slider = Slider(
    ax=ax_win_size,
    label='Window Size',
    valmin=1,
    valmax=20,
    valinit=1,
    valstep=1,
)


# The function to be called anytime a slider's value changes
def update(val):
    predicted = ch12_utils.predict_noise(area[SENSOR], coeff_slider.val, int(win_size_slider.val))
    line.set_ydata(predicted)
    fig.canvas.draw_idle()

    error = target[SENSOR] - predicted
    total_error = (error ** 2).sum()
    print(total_error)


# register the update function with each slider
coeff_slider.on_changed(update)
win_size_slider.on_changed(update)

plt.show()
