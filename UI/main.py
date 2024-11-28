import os

from PyQt5.QtCore import QLibraryInfo

from view import View
from PyQt5.QtWidgets import QApplication
import logging

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)

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
