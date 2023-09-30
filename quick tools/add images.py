from FY3DImage import FY3DImage
import os

folder_path = r"D:\Снимки со спутников\Белые снимки"
name = "Белый снимок"

files = os.listdir(folder_path)
for fname in files:
    fpath = os.path.join(folder_path, fname)
    if fpath.lower().endswith(".hdf"):
        FY3DImage.create(path=fpath, name=name)

