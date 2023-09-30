from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import pyqtSignal
from PIL import Image
from PyQt5.QtGui import QPixmap, QImage
import numpy as np


def set_image_to_label(label, image: Image):
    arr = np.array(image, dtype=np.uint8)
    qimg = QImage(arr.data, image.width, image.height, image.width * 3, QImage.Format_RGB888)
    label.setPixmap(QPixmap(qimg))


class ImageLabel(QLabel):
    presses = list[tuple[int, int]]
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.presses = [(0, 0), (0, 0)]

    def set_image(self, image: Image):
        set_image_to_label(self, image)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.presses.append((ev.x(), ev.y()))
        self.clicked.emit()


