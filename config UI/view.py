from main_window import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtCore import Qt
from ConfigManager import ConfigManager
from FY3DImageManager import FY3DImageManager
import vars
import tasks


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

        for img in self.config.images:
            item = QListWidgetItem(img.name)
            if img.is_used:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_images.addItem(item)

        for task in tasks.IMAGE_TASKS:
            item = QListWidgetItem(task.task_name)
            if task in self.config.image_tasks:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_tasks_images.addItem(item)
        for task in tasks.AREA_TASKS:
            item = QListWidgetItem(task.task_name)
            if task in self.config.area_tasks:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_tasks_areas.addItem(item)

        self.connect_widgets()

    def load_current_image_areas(self):
        img = self.config.images[self.curr_img_index]
        self.ui.listWidget_areas.clear()
        for area in img.areas:
            item = QListWidgetItem(f"x={area.x} y={area.y} w={area.width} h={area.height}")
            if area.is_used:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ui.listWidget_areas.addItem(item)

    def on_img_select(self):
        item = self.ui.listWidget_images.selectedItems()[0]
        self.curr_img_index = self.ui.listWidget_images.row(item)
        self.load_current_image_areas()

    def on_img_changed(self, item: QListWidgetItem):
        index = self.ui.listWidget_images.row(item)
        state = item.checkState()
        if state == Qt.Checked:
            is_used = True
        else:
            is_used = False
        self.config.images[index].is_used = is_used
        self.config.save()

    def on_area_changed(self, item: QListWidgetItem):
        index = self.ui.listWidget_areas.row(item)
        state = item.checkState()
        if state == Qt.Checked:
            is_used = True
        else:
            is_used = False
        self.config.images[self.curr_img_index].areas[index].is_used = is_used
        self.config.save()

    def on_img_task_changed(self, item: QListWidgetItem):
        save_tasks = []
        for i in range(self.ui.listWidget_tasks_images.count()):
            item = self.ui.listWidget_tasks_images.item(i)
            task_name = item.text()
            task = tasks.DICT_IMAGE_TASKS[task_name]
            if item.checkState() == Qt.Checked:
                save_tasks.append(task)
        self.config.image_tasks = save_tasks
        self.config.save()

    def on_area_task_changed(self, item: QListWidgetItem):
        save_tasks = []
        for i in range(self.ui.listWidget_tasks_areas.count()):
            item = self.ui.listWidget_tasks_areas.item(i)
            task_name = item.text()
            task = tasks.DICT_AREA_TASKS[task_name]
            if item.checkState() == Qt.Checked:
                save_tasks.append(task)
        self.config.area_tasks = save_tasks
        self.config.save()

    def on_draw_graphs_changed(self):
        draw_graphs = self.ui.checkBox_draw_graphs.isChecked()
        self.config.draw_graphs = draw_graphs
        self.config.save()

    def on_save_colored_images_changed(self):
        save_colored_image = self.ui.checkBox_save_colored_image.isChecked()
        self.config.save_colored_images = save_colored_image
        self.config.save()

    def on_start_button_clicked(self):
        self.image_manager.run()

    def connect_widgets(self):
        self.ui.listWidget_images.itemSelectionChanged.connect(self.on_img_select)
        self.ui.listWidget_images.itemChanged.connect(self.on_img_changed)
        self.ui.listWidget_areas.itemChanged.connect(self.on_area_changed)
        self.ui.listWidget_tasks_images.itemChanged.connect(self.on_img_task_changed)
        self.ui.listWidget_tasks_areas.itemChanged.connect(self.on_area_task_changed)
        self.ui.checkBox_draw_graphs.stateChanged.connect(self.on_draw_graphs_changed)
        self.ui.checkBox_save_colored_image.stateChanged.connect(self.on_save_colored_images_changed)
        self.ui.pushButton_start.clicked.connect(self.on_start_button_clicked)
