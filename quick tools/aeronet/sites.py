import datetime
import os
from io import StringIO
import tqdm

import pandas as pd

from database import FY3DImage

sites_positions = pd.read_csv("sites_positions.csv", index_col="name")

__data = []
for site_file in tqdm.tqdm(os.listdir("ALL_POINTS")):
    with open("ALL_POINTS/" + site_file) as f:
        # Skipping 6 first lines
        for _ in range(6):
            f.readline()

        data = StringIO(f.read())
        __data.append(pd.read_csv(data))

sites_data = pd.concat(__data)

sites_data["Datetime"] = pd.to_datetime(
    sites_data["Date(dd-mm-yyyy)"] + " " + sites_data["Time(hh:mm:ss)"],
    format="%d:%m:%Y %H:%M:%S"
)


def get_closest_date_data(site_name: str, dt: datetime.datetime) -> pd.Series:
    site_data = sites_data[sites_data["AERONET_Site_Name"] == site_name]
    i = abs(site_data["Datetime"] - dt).argmin()
    return site_data.loc[i]


def get_image_site_data(site_name: str, image: FY3DImage) -> pd.Series:
    img_date = image.get_datetime()
    return get_closest_date_data(site_name, img_date)


def get_site_pos(site_name: str) -> tuple[float, float]:  # lat, lon
    row = sites_positions.loc[site_name]
    return row["lat"], row["lon"]


# sites_data[["AERONET_Site_Name", "Datetime"]].groupby(["AERONET_Site_Name"]).agg(["min", "max"]).to_excel(
#     "Time range.xlsx")
