from database import FY3DImage
import os

output_path = r"C:\Users\Gleb\PycharmProjects\FY3D-images-analyzer\quick tools\area img"
img_id = 5
img = FY3DImage.FY3DImage.get(id=img_id)

width = 100
height = 100

# areas = [
#     (0, 1000 - height),
#     (1000 - width, 1000 - height),
#     (2000 - width, 1000 - height)
# ]

areas = [
    (878, 860),
    (1050, 770)
]


os.mkdir(os.path.join(output_path))
for i, (x, y) in enumerate(areas):
    area = img.get_area(x, y, width, height)
    dir_path = os.path.join(output_path, str(i))
    os.mkdir(dir_path)
    area.save_channels_img_to_dir(dir_path)
    area.cached_data.clear()