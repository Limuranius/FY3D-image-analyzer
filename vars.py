from os import path
from enum import Enum

BASE_DIR = path.dirname(__file__)

CONFIG_PATH = path.join(BASE_DIR, "config.json")
COLORED_PICTURES_PATH = path.join(BASE_DIR, "Изображения/Цветные")
MONOCHROME_PICTURES_PATH = path.join(BASE_DIR, "Изображения/Однотонные")

EXTENSIONS = [".txt", ".xlsx", ".png"]

RESULTS_DIR = path.join(BASE_DIR, "Результаты")


KMIRROR_SIDE = 2  # TODO: перенести эту ебань в config


class SurfaceType(Enum):
    SEA = 1
    SNOW = 2
    UNKNOWN = 3


class KMirrorSide(Enum):
    SIDE_1 = 1
    SIDE_2 = 2
    MIXED = 3