from main_window import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem, QFileDialog, QTreeWidgetItem
from PyQt5.QtCore import Qt
from ConfigManager import ConfigManager
from FY3DImageManager import FY3DImageManager
from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
import vars
from tasks import AreaTasks, ImageTasks, MultipleImagesTasks
from utils.some_utils import *
from FY3DImage import FY3DImage
import areaViewerView
from utils import getImageMonotone
import pickle
from utils import area_utils
import multiprocessing
from utils import some_utils


class View(QMainWindow):
    config: ConfigManager
    image_manager: FY3DImageManager

    curr_img: FY3DImage
    curr_area: FY3DImageArea

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.config = ConfigManager(vars.CONFIG_PATH)
        self.image_manager = FY3DImageManager(self.config)
        self.setup()
        self.image_manager.load()

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
        """Заполняет список снимков"""
        self.ui.treeWidget_images.clear()
        for img in FY3DImage.select():
            item = QTreeWidgetItem(None)
            item.setText(0, img.name)
            item.setText(1, str(img.get_datetime()))

            item.setData(0, Qt.UserRole, img)
            if img.is_selected:
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
            self.ui.treeWidget_images.addTopLevelItem(item)

    def load_current_image_areas(self):
        """Заполняет список областей выбранного снимка"""
        self.ui.treeWidget_areas.clear()
        for area in self.curr_img.areas:
            item = QTreeWidgetItem(None)
            item.setText(0, str(area.x))
            item.setText(1, str(area.y))
            item.setText(2, area.get_surface_type().name)

            item.setData(0, Qt.UserRole, area)
            if area.is_selected:
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
            self.ui.treeWidget_areas.addTopLevelItem(item)

    def load_current_image(self) -> Image.Image:
        return self.curr_img.get_colored_picture()

    """========================= Функционал виджетов ==============================================================="""

    def on_img_select(self):
        """Выделение изображения"""
        item = self.ui.treeWidget_images.selectedItems()[0]
        self.curr_img = item.data(0, Qt.UserRole)
        self.show_img_preview()
        self.load_current_image_areas()

    def on_area_select(self):
        """Выделение области"""
        items = self.ui.treeWidget_areas.selectedItems()
        if items:  # Если что-то выделили
            self.ui.pushButton_del_area.setEnabled(True)
            self.curr_area = items[0].data(0, Qt.UserRole)
        else:  # Если выделение исчезло
            self.ui.pushButton_del_area.setEnabled(False)

    def on_img_changed(self, item: QTreeWidgetItem):
        """Переключение выбора изображений"""
        state = item.checkState(0)
        if state == Qt.Checked:
            is_selected = True
        else:
            is_selected = False
        img = item.data(0, Qt.UserRole)
        img.is_selected = is_selected
        img.save()

    def on_area_changed(self, item: QTreeWidgetItem):
        """Переключение выбора областей"""
        state = item.checkState(0)
        if state == Qt.Checked:
            is_selected = True
        else:
            is_selected = False
        area = item.data(0, Qt.UserRole)
        area.is_selected = is_selected
        area.save()

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

    def on_year_comboBox_changed(self, value):
        """Переключение года снимков"""
        for image in FY3DImage.all_images():
            image.is_selected = image.get_year() == int(value)
            image.save()
        self.update_image_list()

    def on_start_button_clicked(self):
        """Нажатие "Запустить анализ!" """
        self.image_manager.run()

    def on_add_area_button_clicked(self):
        """Нажатие "Добавить область" """
        x = self.ui.spinBox_add_area_x.value()
        y = self.ui.spinBox_add_area_y.value()
        w = self.ui.spinBox_add_area_width.value()
        h = self.ui.spinBox_add_area_height.value()
        FY3DImageArea.create(x=x, y=y, width=w, height=h, image=self.curr_img)
        self.load_current_image_areas()

    def on_del_area_button_clicked(self):
        """Нажатие "Удалить область" """
        self.curr_area.delete_instance()
        self.load_current_image_areas()
        self.show_img_preview()

    def del_all_areas_clicked(self):
        """Нажатие "Удалить все области" """
        FY3DImageArea.delete().where(FY3DImageArea.image == self.curr_img).execute()
        self.load_current_image_areas()
        self.show_img_preview()

    def on_add_mono_areas_clicked(self):
        """Нажатие "Найти однородные области" """
        x_min = self.ui.spinBox_xmin.value()
        x_max = self.ui.spinBox_xmax.value()
        y_min = self.ui.spinBox_ymin.value()
        y_max = self.ui.spinBox_ymax.value()
        count = self.ui.spinBox_areas_count.value()
        max_std = self.ui.spinBox_max_std.value()
        areas = getImageMonotone.get_monotone_areas(
            pickle.loads(self.curr_img.std_sum_map), count=count,
            x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, max_std=max_std)
        insert_data = []
        for x, y in areas:
            insert_data.append({"x": x, "y": y, "width": 100, "height": 10, "image": self.curr_img,
                                "k_mirror_side": area_utils.get_area_mirror_side(y, 10).value})
        FY3DImageArea.insert_many(insert_data).execute()
        self.load_current_image_areas()
        self.show_img_preview()

    def open_area_clicked(self):
        """Нажатие "Открыть область" """
        self.w = areaViewerView.AreaViewerView(self.curr_area)
        self.w.show()

    def see_image_clicked(self):
        """Нажатие "Смотреть изображение" """
        img = self.load_current_image()
        show_im_process = multiprocessing.Process(target=img.show)
        show_im_process.start()

    def img_path_clicked(self):
        """Нажатие "Путь" у снимков """
        file_path = QFileDialog.getOpenFileName(self, "Найти снимок")[0]
        self.ui.lineEdit_img_path.setText(file_path)

    def add_img_clicked(self):
        """Нажатие "Добавить снимок" """
        path = self.ui.lineEdit_img_path.text()
        name = self.ui.lineEdit_img_name.text()
        FY3DImage.create(path=path, name=name)
        self.update_image_list()

    def show_img_preview(self):
        preview = self.curr_img.get_preview()
        x0 = self.ui.spinBox_xmin.value() // vars.PREVIEW_COMPRESS_FACTOR
        x1 = self.ui.spinBox_xmax.value() // vars.PREVIEW_COMPRESS_FACTOR
        y0 = self.ui.spinBox_ymin.value() // vars.PREVIEW_COMPRESS_FACTOR
        y1 = self.ui.spinBox_ymax.value() // vars.PREVIEW_COMPRESS_FACTOR
        some_utils.draw_rectangle(preview, x0, y0, x1 - x0, y1 - y0, "#f8fc03")
        self.ui.label_preview.set_image(preview)

    def preview_clicked(self):
        p1 = self.ui.label_preview.presses[-1]
        p2 = self.ui.label_preview.presses[-2]
        min_x = min(p1[0], p2[0])
        max_x = max(p1[0], p2[0])
        min_y = min(p1[1], p2[1])
        max_y = max(p1[1], p2[1])
        self.ui.spinBox_xmin.setValue(min_x * vars.PREVIEW_COMPRESS_FACTOR)
        self.ui.spinBox_xmax.setValue(max_x * vars.PREVIEW_COMPRESS_FACTOR)
        self.ui.spinBox_ymin.setValue(min_y * vars.PREVIEW_COMPRESS_FACTOR)
        self.ui.spinBox_ymax.setValue(max_y * vars.PREVIEW_COMPRESS_FACTOR)
        self.show_img_preview()

    def all_sea_clicked(self):
        FY3DImageArea.update(surface_type=vars.SurfaceType.SEA.value).where(FY3DImageArea.image == self.curr_img).execute()
        self.load_current_image_areas()

    def all_snow_clicked(self):
        FY3DImageArea.update(surface_type=vars.SurfaceType.SNOW.value).where(FY3DImageArea.image == self.curr_img).execute()
        self.load_current_image_areas()

    def connect_widgets(self):
        self.ui.treeWidget_images.itemSelectionChanged.connect(self.on_img_select)
        self.ui.treeWidget_areas.itemSelectionChanged.connect(self.on_area_select)
        self.ui.treeWidget_images.itemChanged.connect(self.on_img_changed)
        self.ui.treeWidget_areas.itemChanged.connect(self.on_area_changed)
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
        self.ui.comboBox_year.currentTextChanged.connect(self.on_year_comboBox_changed)
        self.ui.label_preview.clicked.connect(self.preview_clicked)
        self.ui.pushButton_all_sea.clicked.connect(self.all_sea_clicked)
        self.ui.pushButton_all_snow.clicked.connect(self.all_snow_clicked)
