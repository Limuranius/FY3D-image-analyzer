import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


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
                           title: str = "", xlabel: str = "", ylabel: str = "", lim: tuple[float, float] = None,
                           legend: list = None, legend_title: str = "", fmt_list: list[str] = None, text: str = ""):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if lim:
        ax.set_ylim(lim)
    if fmt_list is None:
        fmt_list = ["-"] * len(y_rows)
    if x_rows is None:
        for y, fmt in zip(y_rows, fmt_list):
            x = list(range(len(y)))
            ax.plot(x, y, fmt)
    else:
        for x, y, fmt in zip(x_rows, y_rows, fmt_list):
            ax.plot(x, y, fmt)
    if legend:
        ax.legend(legend, title=legend_title, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1))
    ax.text(0.5, 0.1, text, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
            fontsize=12)
    fig.savefig(fig_path)
    plt.close(fig)
