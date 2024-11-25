from io import StringIO
import pandas as pd
from tqdm import tqdm
import paths
import os

with open("create data/good_sites.csv") as f:
    GOOD_SITES = f.read().split()
    GOOD_SITES = list(map(lambda s: s.lower(), GOOD_SITES))


def aeronet_file_to_df(file_path: str) -> pd.DataFrame:
    with open(file_path) as f:
        for _ in range(6):
            f.readline()

        data = StringIO(f.read())
        return pd.read_csv(data)


def load_no_phase() -> pd.DataFrame:
    files = os.listdir(paths.AEROSOL_PATH)

    def filt(file_name: str):
        site = file_name[18:-4].lower()
        return site in GOOD_SITES

    files = list(filter(filt, files))
    files = [os.path.join(paths.AEROSOL_PATH, file) for file in files]

    dfs = []
    for file in tqdm(files, desc="Loading aerosol files to dataframe..."):
        dfs.append(aeronet_file_to_df(file))
    data = pd.concat(dfs)
    data["Datetime"] = pd.to_datetime(
        data["Date(dd:mm:yyyy)"] + " " + data["Time(hh:mm:ss)"],
        format="%d:%m:%Y %H:%M:%S"
    )
    return data


def load_phase() -> pd.DataFrame:
    files = os.listdir(paths.AEROSOL_PHASE_PATH)

    def filt(file_name: str):
        site = file_name[18:-4].lower()
        return site in GOOD_SITES

    files = list(filter(filt, files))
    files = [os.path.join(paths.AEROSOL_PHASE_PATH, file) for file in files]

    dfs = []
    for file in tqdm(files, desc="Loading aerosol phase functions files to dataframe..."):
        dfs.append(aeronet_file_to_df(file))
    data = pd.concat(dfs)
    data["Datetime"] = pd.to_datetime(
        data["Date(dd:mm:yyyy)"] + " " + data["Time(hh:mm:ss)"],
        format="%d:%m:%Y %H:%M:%S"
    )
    return data


def load_ocean_color() -> pd.DataFrame:
    files = os.listdir(paths.OCEAN_COLOR_PATH)
    sites = [file_name[18:-10] for file_name in files]
    files = [os.path.join(paths.OCEAN_COLOR_PATH, file) for file in files]
    dfs = []
    for file, site in tqdm(
            zip(files, sites),
            desc="Loading ocean color files to dataframe...",
            total=len(files)
    ):
        df = aeronet_file_to_df(file)
        df["Site"] = [site] * len(df)
        dfs.append(df)
    data = pd.concat(dfs)
    data["Datetime"] = pd.to_datetime(
        data["Date(dd-mm-yyyy)"] + " " + data["Time(hh:mm:ss)"],
        format="%d:%m:%Y %H:%M:%S"
    )
    return data
