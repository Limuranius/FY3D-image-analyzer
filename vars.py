from os import path

BASE_DIR = path.dirname(__file__)

CONFIG_PATH = path.join(BASE_DIR, "config.json")
COLORED_PICTURES_PATH = path.join(BASE_DIR, "Изображения/Цветные")
MONOCHROME_PICTURES_PATH = path.join(BASE_DIR, "Изображения/Однотонные")

EXTENSIONS = [".txt", ".xlsx", ".png"]

RESULTS_DIR = path.join(BASE_DIR, "Результаты")


KMIRROR_SIDE = 1  # TODO: перенести эту ебань в config
