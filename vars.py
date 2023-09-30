from os import path
from enum import Enum

ROOT_DIR = path.dirname(__file__)

CONFIG_PATH = path.join(ROOT_DIR, "config.json")
COLORED_PICTURES_PATH = path.join(ROOT_DIR, "Изображения/Цветные")
MONOCHROME_PICTURES_PATH = path.join(ROOT_DIR, "Изображения/Однотонные")
DATABASE_PATH = path.join(ROOT_DIR, "database.db")

RESULTS_DIR = path.join(ROOT_DIR, "Результаты")

PREVIEW_COMPRESS_FACTOR = 4  # Во сколько раз уменьшается изображение для превью в GUI


class SurfaceType(Enum):
    SEA = 1
    SNOW = 2
    UNKNOWN = 3


class KMirrorSide(Enum):
    SIDE_1 = 1
    SIDE_2 = 2
    MIXED = 3
