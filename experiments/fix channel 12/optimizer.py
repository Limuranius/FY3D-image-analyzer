import numpy as np
from scipy.optimize import minimize
import tqdm
from database import FY3DImageArea
import ch12_utils


def get_data() -> tuple[np.ndarray, np.ndarray]:
    # returns area and target noise

    areas_ids = [8934, 8935, 8936, 8937, 8938]
    areas = [FY3DImageArea.get(id=area_id).get_vis_channel(12).astype(int) for area_id in areas_ids]
    targets = [area - sensor12_utils.get_true_sea_values(area) for area in areas]
    return (
        np.concatenate(areas, axis=1),
        np.concatenate(targets, axis=1)
    )


def error_func(coeffs, win_size, sensor, target_values, area) -> float:
    row = area[sensor]
    predicted_noise = sensor12_utils.predict_noise(row, coeffs[0], win_size)
    error = target_values[sensor] - predicted_noise
    total_error = (error ** 2).sum()
    return total_error


def main():
    area, target = get_data()

    sensor_params = []
    for sensor in range(10):
        results = [
            (
                minimize(
                    error_func,
                    x0=[0],
                    args=(win_size, sensor, target, area),
                    bounds=((0, 0.005),)
                ),
                win_size
            )
            for win_size in range(8, 25)
        ]
        # print([(x[1], x[0].fun, x[0].x[0]) for x in results])
        min_result = min(results, key=lambda x: x[0].fun)
        sensor_params.append((min_result[1], min_result[0].x[0]))
    print(sensor_params)

    with open("data/new_coeffs.txt", "w") as f:
        for win_size, coeff in sensor_params:
            f.write(f"{win_size} {coeff}\n")

main()
