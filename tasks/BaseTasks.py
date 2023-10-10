from abc import ABC, abstractmethod
import pandas as pd


class BaseTask(ABC):
    task_name: str
    result: pd.DataFrame | dict[str, pd.DataFrame]

    def get_data(self) -> pd.DataFrame:
        if not hasattr(self, "result"):
            self.calculate_data()
        return self.result

    @abstractmethod
    def calculate_data(self) -> None:
        pass

    def accept(self, visitor):
        visitor.visit(self)

    def save_to_excel(self):
        from tasks.ExcelVisitor import ExcelVisitor
        self.accept(ExcelVisitor())

    def save_to_graphs(self):
        from tasks.GraphsVisitor import GraphsVisitor
        self.accept(GraphsVisitor())
