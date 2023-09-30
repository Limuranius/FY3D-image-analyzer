import numpy as np
from PIL import Image, ImageDraw
import os
import shutil
import cv2


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


def draw_rectangle(image: Image, x: int, y: int, width: int, height: int, color: str):
    drawer = ImageDraw.Draw(image)
    shape = (x, y, x + width, y + height)
    if is_image_colored(image):
        drawer.rectangle(shape, outline=color)
    else:
        drawer.rectangle(shape, fill="#FFFFFF")


def increase_brightness(img: Image, value=40) -> Image:
    img_arr = np.array(img)
    hsv = cv2.cvtColor(img_arr, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img_arr = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2RGB)
    img = Image.fromarray(img_arr)
    return img

