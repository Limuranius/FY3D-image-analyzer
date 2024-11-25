from database import FY3DImageArea
import pandas as pd

ids = [8932, 8930, 8931]
channels = [8, 10]

areas: list[FY3DImageArea] = [FY3DImageArea.get(id=area_id) for area_id in ids]

with pd.ExcelWriter("Areas.xlsx") as writer:
    for channel in channels:
        for area in areas:
            ch_area = area.get_vis_channel(channel)
            df = pd.DataFrame(ch_area)
            df.to_excel(writer, sheet_name=f"ch={channel} id={area.id}", index=False, header=False)
