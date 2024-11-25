import numpy as np
import rasterio
from rasterio.control import GroundControlPoint
from database import FY3DImage

img: FY3DImage = FY3DImage.get(id=10)
lon_grid = img.Longitude
lat_grid = img.Latitude
h, w = lon_grid.shape


points = []
for i in range(h):
    for j in range(w):
        col = j * 5
        row = i * 5
        lon = lon_grid[i, j]
        lat = lat_grid[i, j]
        gcp = GroundControlPoint(row=row, col=col, x=lon, y=lat)
        points.append(gcp)

transformation = rasterio.transform.from_gcps(points)

with rasterio.open(
    "output.tif",
    "w",
    driver="GTiff",
    height=2000,
    width=2048,
    count=15,
    dtype=np.uint16,
    crs=rasterio.crs.CRS().from_epsg(4326),
    transform=transformation
) as output:
    for channel in range(5, 20):
        output.write(img.get_vis_channel(channel), channel - 4)
