from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from main_window import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
from ConfigManager import ConfigManager
from FY3DImageManager import FY3DImageManager
import vars
from tasks import AreaTasks, ImageTasks, MultipleImagesTasks
from utils.getImageMonotone import get_min_monotone
from utils.utils import *
from FY3DImage import FY3DImage
import areaViewerView


def set_image_to_label(label, image: Image.Image):
    qtimg = ImageQt.ImageQt(image)
    label.setPixmap(QPixmap.fromImage(qtimg))


class View(QMainWindow):
    config: ConfigManager
    image_manager: FY3DImageManager

    curr_img_index: int
    curr_area_index: int

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.config = ConfigManager(vars.CONFIG_PATH)
        self.image_manager = FY3DImageManager(self.config)
        self.setup()

    def setup(self):
        self.ui.checkBox_draw_graphs.setChecked(self.config.draw_graphs)
        self.ui.checkBox_save_colored_image.setChecked(self.config.save_colored_images)

        self.update_image_list()

        for task in ImageTasks.IMAGE_TASKS:
            item = QListWidgetItem(task.task_name)
            if task in self.config.image_tasks:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_tasks_images.addItem(item)
        for task in AreaTasks.AREA_TASKS:
            item = QListWidgetItem(task.task_name)
            if task in self.config.area_tasks:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_tasks_areas.addItem(item)
        for task in MultipleImagesTasks.MULTI_IMAGE_TASKS:
            item = QListWidgetItem(task.task_name)
            if task in self.config.multi_image_tasks:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_tasks_multi_images.addItem(item)

        self.connect_widgets()

    def update_image_list(self):
        self.ui.listWidget_images.clear()
        for img in self.config.images:
            item = QListWidgetItem(img.name)
            if img.is_used:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_images.addItem(item)

    def load_current_image_areas(self):
        img_info = self.config.images[self.curr_img_index]
        self.ui.listWidget_areas.clear()
        for area_info in img_info.areas:
            item = QListWidgetItem(f"x={area_info.x} y={area_info.y} w={area_info.width} h={area_info.height}")
            if area_info.is_used:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_areas.addItem(item)

    def load_current_image(self) -> Image.Image:
        img_info = self.config.images[self.curr_img_index]
        img = FY3DImage(img_info.path)
        for area_info in img_info.areas:
            if area_info.is_used:
                img.add_area(area_info.x, area_info.y, area_info.width, area_info.height)
        return img.get_colored_picture()

    """========================= Функционал виджетов ==============================================================="""
    def on_img_select(self):
        """Выделение изображения"""
        item = self.ui.listWidget_images.selectedItems()[0]
        self.curr_img_index = self.ui.listWidget_images.row(item)
        self.load_current_image_areas()

    def on_area_select(self):
        """Выделение области"""
        items = self.ui.listWidget_areas.selectedItems()
        if items:  # Если что-то выделили
            self.ui.pushButton_del_area.setEnabled(True)
            self.curr_area_index = self.ui.listWidget_areas.row(items[0])
        else:  # Если выделение исчезло
            self.ui.pushButton_del_area.setEnabled(False)

    def on_img_changed(self, item: QListWidgetItem):
        """Переключение выбора изображений"""
        index = self.ui.listWidget_images.row(item)
        state = item.checkState()
        if state == Qt.Checked:
            is_used = True
        else:
            is_used = False
        self.config.images[index].is_used = is_used
        self.config.save()

    def on_area_changed(self, item: QListWidgetItem):
        """Переключение выбора областей"""
        index = self.ui.listWidget_areas.row(item)
        state = item.checkState()
        if state == Qt.Checked:
            is_used = True
        else:
            is_used = False
        self.config.images[self.curr_img_index].areas[index].is_used = is_used
        self.config.save()

    def on_img_task_changed(self, item: QListWidgetItem):
        """Изменение выбора методов изображений"""
        save_tasks = []
        for i in range(self.ui.listWidget_tasks_images.count()):
            item = self.ui.listWidget_tasks_images.item(i)
            task_name = item.text()
            task = ImageTasks.DICT_IMAGE_TASKS[task_name]
            if item.checkState() == Qt.Checked:
                save_tasks.append(task)
        self.config.image_tasks = save_tasks
        self.config.save()

    def on_area_task_changed(self, item: QListWidgetItem):
        """Изменение выбора методов областей"""
        save_tasks = []
        for i in range(self.ui.listWidget_tasks_areas.count()):
            item = self.ui.listWidget_tasks_areas.item(i)
            task_name = item.text()
            task = AreaTasks.DICT_AREA_TASKS[task_name]
            if item.checkState() == Qt.Checked:
                save_tasks.append(task)
        self.config.area_tasks = save_tasks
        self.config.save()

    def on_multi_img_task_changed(self, item: QListWidgetItem):
        """Изменение выбора методов мульти-изображений"""
        save_tasks = []
        for i in range(self.ui.listWidget_tasks_multi_images.count()):
            item = self.ui.listWidget_tasks_multi_images.item(i)
            task_name = item.text()
            task = MultipleImagesTasks.DICT_MULTI_IMAGE_TASKS[task_name]
            if item.checkState() == Qt.Checked:
                save_tasks.append(task)
        self.config.multi_image_tasks = save_tasks
        self.config.save()

    def on_draw_graphs_changed(self):
        """Переключение "Рисовать графики" """
        draw_graphs = self.ui.checkBox_draw_graphs.isChecked()
        self.config.draw_graphs = draw_graphs
        self.config.save()

    def on_save_colored_images_changed(self):
        """Переключение "Сохранять изображения снимков" """
        save_colored_image = self.ui.checkBox_save_colored_image.isChecked()
        self.config.save_colored_images = save_colored_image
        self.config.save()

    def on_start_button_clicked(self):
        """Нажатие "Запустить анализ!" """
        self.image_manager.run()

    def on_add_area_button_clicked(self):
        """Нажатие "Добавить область" """
        x = self.ui.spinBox_add_area_x.value()
        y = self.ui.spinBox_add_area_y.value()
        w = self.ui.spinBox_add_area_width.value()
        h = self.ui.spinBox_add_area_height.value()
        self.config.images[self.curr_img_index].add_area(x, y, w, h)
        self.config.save()
        self.load_current_image_areas()

    def on_del_area_button_clicked(self):
        """Нажатие "Удалить область" """
        self.config.del_area(self.curr_img_index, self.curr_area_index)
        self.config.save()
        self.load_current_image_areas()

    def del_all_areas_clicked(self):
        """Нажатие "Удалить все области" """
        while self.config.areas_count(self.curr_img_index) > 0:
            self.config.del_area(self.curr_img_index, 0)
        self.config.save()
        self.load_current_image_areas()

    def on_add_mono_areas_clicked(self):
        """Нажатие "Найти однородные области" """
        img_info = self.config.images[self.curr_img_index]
        image = FY3DImage(img_info.path, img_info.name)
        x_min = self.ui.spinBox_xmin.value()
        x_max = self.ui.spinBox_xmax.value()
        y_min = self.ui.spinBox_ymin.value()
        y_max = self.ui.spinBox_ymax.value()
        areas = get_min_monotone(image, 20, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
        h = 10
        w = 100
        for x, y in areas:
            self.config.images[self.curr_img_index].add_area(x, y, w, h)
        self.config.save()
        self.load_current_image_areas()

    def open_area_clicked(self):
        """Нажатие "Открыть область" """
        img_info = self.config.images[self.curr_img_index]
        area_info = img_info.areas[self.curr_area_index]

        img = FY3DImage(img_info.path)
        img.add_area(area_info.x, area_info.y, area_info.width, area_info.height)

        area = img.areas[0]
        self.w = areaViewerView.AreaViewerView(area)
        self.w.show()

    def see_image_clicked(self):
        """Нажатие "Смотреть изображение" """
        self.load_current_image().show()

    def img_path_clicked(self):
        """Нажатие "Путь" у снимков """
        file_path = QFileDialog.getOpenFileName(self, "Найти снимок", "C:\\Users\\Gleb\Desktop\\Диплом\\Снимки со спутников")[0]
        self.ui.lineEdit_img_path.setText(file_path)

    def add_img_clicked(self):
        """Нажатие "Добавить снимок" """
        file_path = self.ui.lineEdit_img_path.text()
        file_name = self.ui.lineEdit_img_name.text()
        self.config.add_image(file_path, file_name)
        self.config.save()
        self.update_image_list()

    def connect_widgets(self):
        self.ui.listWidget_images.itemSelectionChanged.connect(self.on_img_select)
        self.ui.listWidget_areas.itemSelectionChanged.connect(self.on_area_select)
        self.ui.listWidget_images.itemChanged.connect(self.on_img_changed)
        self.ui.listWidget_areas.itemChanged.connect(self.on_area_changed)
        self.ui.listWidget_tasks_images.itemChanged.connect(self.on_img_task_changed)
        self.ui.listWidget_tasks_areas.itemChanged.connect(self.on_area_task_changed)
        self.ui.listWidget_tasks_multi_images.itemChanged.connect(self.on_multi_img_task_changed)
        self.ui.checkBox_draw_graphs.stateChanged.connect(self.on_draw_graphs_changed)
        self.ui.checkBox_save_colored_image.stateChanged.connect(self.on_save_colored_images_changed)
        self.ui.pushButton_start.clicked.connect(self.on_start_button_clicked)
        self.ui.pushButton_add_area.clicked.connect(self.on_add_area_button_clicked)
        self.ui.pushButton_del_area.clicked.connect(self.on_del_area_button_clicked)
        self.ui.pushButton_del_all_areas.clicked.connect(self.del_all_areas_clicked)
        self.ui.pushButton_add_monotone_areas.clicked.connect(self.on_add_mono_areas_clicked)
        self.ui.pushButton_open_area.clicked.connect(self.open_area_clicked)
        self.ui.pushButton_see_image.clicked.connect(self.see_image_clicked)
        self.ui.pushButton_img_path.clicked.connect(self.img_path_clicked)
        self.ui.pushButton_add_image.clicked.connect(self.add_img_clicked)


