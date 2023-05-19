import os
from abc import ABC, abstractmethod
import vars
import pandas as pd
from utils import utils


class BaseTask(ABC):
    task_name: str
    root_dir: str
    obj_name: str

    excel_dir_path: str
    graphs_dir_path: str

    def __init__(self):
        self.root_dir = os.path.join(vars.RESULTS_DIR, self.task_name)
        self.excel_dir_path = os.path.join(self.root_dir, "Excel таблицы")
        utils.create_dir(self.excel_dir_path)
        self.graphs_dir_path = os.path.join(self.root_dir, "Графики")
        utils.create_dir(self.graphs_dir_path)

    def run(self, draw_graphs: bool = False):
        data = self.calculate_data()
        if draw_graphs:
            self.save_graphs(data)
        self.save_excel(data)

    @abstractmethod
    def calculate_data(self):
        pass

    def save_excel(self, data):
        pass

    def save_graphs(self, data):
        pass

    def get_excel_path(self, file_name: str):
        return os.path.join(self.excel_dir_path, file_name + ".xlsx")

    def get_graph_img_path(self, file_name: str):
        return os.path.join(self.graphs_dir_path, file_name + ".png")


