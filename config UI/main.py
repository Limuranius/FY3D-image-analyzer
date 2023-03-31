from view import View
from PyQt5.QtWidgets import QApplication
import logging


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s\t%(message)s",
        datefmt="%d-%m-%Y %H:%M:%S"
    )
    app = QApplication([])
    window = View()
    window.show()
    app.exec_()
