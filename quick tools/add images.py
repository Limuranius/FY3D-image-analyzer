from database.FY3DImage import FY3DImage
import os

folder_path = r"D:\Снимки со спутников\2021 2"
name = "2021 2"

files = os.listdir(folder_path)
for fname in files:
    fpath = os.path.join(folder_path, fname)
    if fpath.lower().endswith(".hdf"):
        img = FY3DImage(path=fpath, name=name)
        img.year = img.get_year()
        img.save()

