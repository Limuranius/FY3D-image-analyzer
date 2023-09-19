from abc import ABC, abstractmethod
import pandas as pd


class BaseTask(ABC):
    task_name: str
    result: pd.DataFrame

    def run(self) -> None:
        self.result = self.calculate_data()

    def get_data(self) -> pd.DataFrame:
        if not hasattr(self, "result"):
            self.run()
        return self.result

    @abstractmethod
    def calculate_data(self) -> pd.DataFrame:
        pass

    def accept(self, visitor):
        visitor.visit(self)

    def save_to_excel(self):
        from tasks.ExcelVisitor import ExcelVisitor
        self.accept(ExcelVisitor())

    def save_to_graphs(self):
        from tasks.GraphsVisitor import GraphsVisitor
        self.accept(GraphsVisitor())
