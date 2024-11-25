import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider
from database import FY3DImage, FY3DImageArea
import ch12_utils


def get_data() -> tuple[np.ndarray, np.ndarray]:
    # returns area and target noise

    areas_ids = [
        8934,
        8935,
        8936,
        8937,
        8938
    ]
    areas = [FY3DImageArea.get(id=area_id).get_vis_channel(12).astype(int) for area_id in areas_ids]
    targets = [area - sensor12_utils.get_true_sea_values(area) for area in areas]
    return (
        np.concatenate(areas, axis=1),
        np.concatenate(targets, axis=1)
    )


curr_sensor = 0
area, target = get_data()

# Create the figure and the line that we will manipulate
fig, (ax, ax1) = plt.subplots(ncols=2, width_ratios=[3, 1])
ax.set_xlabel("x")
ax.set_ylabel("Остаточный сигнал")
ax.grid()

line_target = ax.plot(target[curr_sensor])[0]
line_predicted = ax.plot(sensor12_utils.predict_noise(area[curr_sensor], 0, 1))[0]
line_error = ax1.plot([0] * 100)[0]

# adjust the main plot to make room for the sliders
fig.subplots_adjust(bottom=0.25)

# Make a horizontal slider to control the frequency.
ax_coeff = fig.add_axes([0.25, 0.1, 0.65, 0.03])
coeff_slider = Slider(
    ax=ax_coeff,
    label='Coeff',
    valmin=0,
    valmax=0.003,
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

errors = [0] * 100

# The function to be called anytime a slider's value changes
def update(val):
    predicted = sensor12_utils.predict_noise(area[curr_sensor], coeff_slider.val, int(win_size_slider.val))
    line_predicted.set_ydata(predicted)
    line_target.set_ydata(target[curr_sensor])

    error = target[curr_sensor] - predicted
    total_error = (error ** 2).sum()
    errors.append(total_error)
    line_error.set_ydata(errors[-100:])
    ax1.relim()
    ax1.autoscale_view()

    fig.canvas.draw_idle()



# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
next_sensor_ax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
button = Button(next_sensor_ax, 'Next sensor', hovercolor='0.975')

coeffs = []


def next_sensor(event):
    global curr_sensor
    curr_sensor += 1
    ax.set_title(f"Sensor {curr_sensor}")
    coeffs.append((int(win_size_slider.val), coeff_slider.val))
    if curr_sensor >= 10:
        print(coeffs)
        with open("data/manual_coeffs.txt", "w") as f:
            for win_size, coeff in coeffs:
                f.write(f"{win_size} {coeff}\n")
        plt.close()
    else:
        coeff_slider.reset()
        win_size_slider.reset()
        global errors
        errors = [0] * 100
        update(0)


button.on_clicked(next_sensor)
coeff_slider.on_changed(update)
win_size_slider.on_changed(update)

plt.show()
