import numpy as np
import pandas as pd
import matplotlib as plt
import os
from .utils import create_dir


def save_excel(path: str, sheets: list[tuple[str, list | np.ndarray]]):
    create_dir(path)
    with pd.ExcelWriter(path) as writer:
        for sheet_name, sheet_data in sheets:
            df = pd.DataFrame(sheet_data)
            df.to_excel(writer, sheet_name, index=False, header=False)


def create_and_save_figure(fig_path: str, y_rows: list[list[int | float]], x_rows: list[list[int | float]] = None,
                           title: str = "", xlabel: str = "", ylabel: str = "", lim: tuple[float, float] = None,
                           legend: list = None, legend_title: str = ""):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if lim:
        ax.set_ylim(lim)
    if x_rows is None:
        for y in y_rows:
            x = list(range(len(y)))
            ax.plot(x, y)
    else:
        for x, y in zip(x_rows, y_rows):
            ax.plot(x, y)
    if legend:
        ax.legend(legend, title=legend_title, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1))

    create_dir(fig_path)
    fig.savefig(fig_path)
    plt.close(fig)


