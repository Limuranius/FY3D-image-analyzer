import area_viewer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from database.FY3DImageArea import FY3DImageArea
import matplotlib.pyplot as plt
from PIL import Image, ImageQt
import io
from utils import some_utils


def fig_to_img(fig) -> Image:
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    im = Image.open(img_buf)
    im = im.convert("RGB")
    return im


class AreaViewerView(QWidget):
    area: FY3DImageArea

    def __init__(self, area: FY3DImageArea):
        super().__init__()
        self.area = area
        self.ui = area_viewer.Ui_Form()
        self.ui.setupUi(self)
        self.setup()

    def setup(self):
        self.ui.label_area_name.setText(self.area.get_short_name())
        self.ui.pushButton.clicked.connect(self.draw_graphs)

    def draw_graphs(self):
        ch = int(self.ui.comboBox_channel.currentText())
        sensor = int(self.ui.comboBox_sensor.currentText())

        # self.ui.label_col_avg.set_image(self.get_col_avg_graph(ch))
        # self.ui.label_sensor_deviation.set_image(self.get_sensor_deviation_graph(ch, sensor))
        self.ui.label_spectre.set_image(self.get_normalized_spectre_graph())

        ch_area = self.area.get_vis_channel(ch)
        area_avg = ch_area.mean()
        sensor_avg = ch_area[sensor].mean()
        self.ui.label_area_avg.setText(str(area_avg))
        self.ui.label_sensor_avg_dev.setText(str(sensor_avg - area_avg))

    def get_col_avg_graph(self, ch: int):
        ch_area = self.area.get_vis_channel(ch)
        x = list(range(self.area.width))
        y = [ch_area[:, j].mean() for j in x]

        fig, ax = plt.subplots()
        ax.set_title(f"Среднее по столбцу")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Среднее по столбцу")
        ax.plot(x, y)

        img = fig_to_img(fig)
        return img

    def get_sensor_deviation_graph(self, ch: int, sensor: int):
        ch_area = self.area.get_vis_channel(ch)
        area_avg = ch_area.mean()
        x = list(range(self.area.width))
        y = [ch_area[sensor, j] - area_avg for j in x]

        fig, ax = plt.subplots()
        ax.set_title(f"Отклонение датчика от среднего по области")
        ax.set_xlabel("Номер столбца")
        ax.set_ylabel("Отклонение от среднего")
        ax.plot(x, y)

        img = fig_to_img(fig)
        return img

    def get_normalized_spectre_graph(self):
        x = list(range(5, 20))
        y = []
        for channel in range(5, 20):
            ch_area = self.area.get_vis_channel(channel)
            DN = ch_area.mean()
            DN_norm = some_utils.DN_to_Ref(DN, self.area.image, channel)
            y.append(DN_norm)
        fig, ax = plt.subplots()
        ax.set_xlabel("Номер канала")
        ax.set_ylabel("DN_normalized")
        ax.plot(x, y)

        img = fig_to_img(fig)
        return img
