from database import FY3DImage
from collections import defaultdict
from sites import sites_positions

images = FY3DImage.all_images()

contains: dict[int, list[str]] = defaultdict(list)  # image_id: site_names


# 2 5 10 14 19 21 38 62 74 107


def get_image_sites(image: FY3DImage) -> list[str]:
    names = []
    for i, site_row in sites_positions.iterrows():
        if image.contains_pos(site_row["lat"], site_row["lon"]):
            names.append(site_row["name"])
    return names


for image in images:


print(*contains)
