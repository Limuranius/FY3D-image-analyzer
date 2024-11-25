from database import FY3DImage
import timer

img: FY3DImage = FY3DImage.get(id=1)

lat = -18.396230
lon = 121.322864


# print(img.get_closest_pixel(lat, lon))
with timer.timer() as t:
    print(img.contains_pos(lat, lon))
    print(t.elapse)

# img.get_colored_picture().show()