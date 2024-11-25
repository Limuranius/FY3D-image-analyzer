import pandas as pd
from io import StringIO
import os


sites = pd.DataFrame(columns=["name", "lat", "lon"])


for site_file in os.listdir("ALL_POINTS"):
    with open("ALL_POINTS/" + site_file) as f:
        # Skipping 6 first lines
        for _ in range(6):
            f.readline()

        data = StringIO(f.read())
        df = pd.read_csv(data)

    row = df.iloc[0]
    sites.loc[len(sites)] = [
        row["AERONET_Site_Name"],
        row["Site_Latitude(Degrees)"],
        row["Site_Longitude(Degrees)"],
    ]
    # print(len(df[["Site_Latitude(Degrees)", "Site_Longitude(Degrees)"]].value_counts()))


print(sites)
sites.to_csv("sites_positions.csv", index=False)
