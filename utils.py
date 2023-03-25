import numpy as np
from PIL import Image, ImageDraw
import os
import shutil
from vars import EXTENSIONS


def create_dirs(some_path: str):
    for ext in EXTENSIONS:
        if some_path.endswith(ext):  # Путь заканчивается на файл
            some_path = os.path.dirname(some_path)
    os.makedirs(some_path, exist_ok=True)


def remove_dir(dir_path: str):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)


"""
Заметка:
Значения пикселя в снимках хранится в 12 битах
Если надо преобразовывать в изображение, надо уменьшить квантование до 8 бит
"""


def get_monochrome_image(layer: np.ndarray) -> Image:
    layer = layer // 16  # Сжимаем 12 бит до 8 бит
    layer = np.uint8(layer)
    image = Image.fromarray(layer, "L")
    return image


def get_colored_image(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> Image:
    # Сжимаем 12 бит до 8 бит
    r = np.uint8(r // 16)
    g = np.uint8(g // 16)
    b = np.uint8(b // 16)
    stack = np.stack([r, g, b], axis=2)
    image = Image.fromarray(stack, "RGB")
    return image


def is_image_colored(image: Image) -> bool:
    pixel = image.getpixel((0, 0))
    if isinstance(pixel, tuple):
        return True
    else:
        return False


def draw_rectangle(image: Image, x: int, y: int, width: int, height: int):
    drawer = ImageDraw.Draw(image)
    shape = (x, y, x + width, y + height)
    if is_image_colored(image):
        drawer.rectangle(shape, outline="#FF0000")
    else:
        drawer.rectangle(shape, fill="#FFFFFF")


def linregress(x, y, w=None, b=None):
    """Линейная регрессия методом наименьших квадратов"""
    x = np.array(x, dtype=np.float64)
    y = np.array(y, dtype=np.float64)

    if w is None:
        w = np.ones(x.size, dtype=np.float64)

    wxy = np.sum(w*y*x)
    wx = np.sum(w*x)
    wy = np.sum(w*y)
    wx2 = np.sum(w*x*x)
    sw = np.sum(w)

    den = wx2*sw - wx*wx

    if den == 0:
        den = np.finfo(np.float64).eps

    if b is None:
        k = (sw*wxy - wx*wy) / den
        b = (wy - k*wx) / sw
    else:
        k = (wxy - wx*b) / wx2

    return k, b