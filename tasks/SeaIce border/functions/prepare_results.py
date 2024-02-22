import os

import numpy as np
import pandas as pd
import visual
import filter_image
import timeresults
from os import path
import sensors_relation
import pickle


def prepare_results(
        name: str,
        a_coeffs: np.ndarray,
        b1_coeffs: np.ndarray,
        b2_coeffs: np.ndarray,
        areas_ids: list[int],
        func_values_df: pd.DataFrame | None,
        image: np.ndarray,
        image_areas: list[tuple[int, int, int, int, int, int]]
) -> None:
    coeffs = np.empty(shape=(10, 30))
    coeffs[:, 0:10] = a_coeffs
    coeffs[:, 10:20] = b1_coeffs
    coeffs[:, 20:30] = b2_coeffs

    folder = timeresults.get_session_path(name)
    os.makedirs(folder, exist_ok=True)

    if func_values_df is not None:
        # График уменьшения функции ошибки
        visual.func_values(
            df=func_values_df,
            path=path.join(folder, "Прогресс оптимизации")
        )

        # pickle файл со значениями функций
        func_values_df.to_pickle(
            path.join(folder, "Прогресс оптимизации.pickle")
        )

    # Графики приближения для каждого датчика
    visual.visualize_all(
        coeffs=coeffs,
        ids=areas_ids,
        path=path.join(folder, "Графики приближения")
    )

    # Гистограмма соотношений датчиков после калибровки
    # relation_data = sensors_relation.collect_data(coeffs)
    # visual.visualize_sensors_relation(
    #     df=relation_data,
    #     path=path.join(folder, "Отношение датчиков")
    # )

    # Изображения части снимка после калибровки
    filtered_img = filter_image.filter_area(image, coeffs)
    os.makedirs(path.join(folder, "Отфильтрованные изображения"), exist_ok=True)
    for i, (x, y, w, h, min_value, max_value) in enumerate(image_areas):
        img_path = path.join(folder, "Отфильтрованные изображения", f"{i}.png")
        visual.save_contrasted_area(
            image_channel=filtered_img,
            path=img_path,
            x=x, y=y, w=w, h=h,
            min_value=min_value,
            max_value=max_value,
        )

    # Excel и pickle файл с коэффициентами
    with pd.ExcelWriter(path=path.join(folder, "Коэффициенты.xlsx")) as writer:
        pd.DataFrame(a_coeffs).to_excel(
            excel_writer=writer,
            sheet_name="a",
            header=False,
            index=False
        )
        pd.DataFrame(b1_coeffs).to_excel(
            excel_writer=writer,
            sheet_name="b1",
            header=False,
            index=False
        )
        pd.DataFrame(b2_coeffs).to_excel(
            excel_writer=writer,
            sheet_name="b2",
            header=False,
            index=False
        )
    with open("Коэффициенты.pickle", "wb") as f:
        pickle.dump([a_coeffs, b1_coeffs, b2_coeffs], f)

    # Визуализация коэффициентов
    visual.visualize_coeffs(a_coeffs, path.join(folder, "Коэффициенты a.png"))
    visual.visualize_coeffs(b1_coeffs, path.join(folder, "Коэффициенты b1.png"))
    visual.visualize_coeffs(b2_coeffs, path.join(folder, "Коэффициенты b2.png"))
