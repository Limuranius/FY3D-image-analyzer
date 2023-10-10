import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageOps, ImageDraw, ImageFont
import os


def save_excel(path: str, sheets: list[tuple[str, list | np.ndarray]]):
    with pd.ExcelWriter(path) as writer:
        for sheet_name, sheet_data in sheets:
            df = pd.DataFrame(sheet_data)
            df.to_excel(writer, sheet_name, index=False, header=False)


def save_excel_dataframe(path: str, sheets: list[tuple[str, pd.DataFrame]], index: bool = False, header: bool = False):
    with pd.ExcelWriter(path) as writer:
        for sheet_name, sheet_data in sheets:
            sheet_data.to_excel(writer, sheet_name, index=index, header=header)


def create_and_save_figure(fig_path: str, y_rows: list[list[int | float]], x_rows: list[list[int | float]] = None,
                           title: str = "", xlabel: str = "", ylabel: str = "",
                           ylim: tuple[float, float] = None, xlim: tuple[float, float] = None,
                           legend: list = None, legend_title: str = "", fmt_list: list[str] = None, text: str = "",
                           markersize: float = 3):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(ylim)
    if xlim:
        ax.set_xlim(xlim)
    if fmt_list is None:
        fmt_list = ["-"] * len(y_rows)
    if x_rows is None:
        for y, fmt in zip(y_rows, fmt_list):
            x = list(range(len(y)))
            ax.plot(x, y, fmt, markersize=markersize)
    else:
        for x, y, fmt in zip(x_rows, y_rows, fmt_list):
            ax.plot(x, y, fmt, markersize=markersize)
    if legend:
        ax.legend(legend, title=legend_title, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1))

    # Пишем текст
    font = ImageFont.truetype("arial.ttf", size=16)
    fig.canvas.draw()
    fig_img = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
    text_space = 250
    fig_img = ImageOps.expand(fig_img, border=(0, 0, text_space, 0), fill=(255, 255, 255))
    drawer = ImageDraw.Draw(fig_img)
    drawer.text((590, 20), text, fill=0, font=font)

    fig_img.save(fig_path)
    plt.close(fig)
