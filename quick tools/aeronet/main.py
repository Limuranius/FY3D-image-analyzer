import tqdm
import pandas as pd
import get_areas
import sites
import process_areas

from database import FY3DImage

CHANNELS = [3, 12]

with pd.ExcelWriter("Results2.xlsx") as writer:
    for channel in CHANNELS:
        df = pd.DataFrame(columns=[
            "image_id",
            "site_name",
            "satellite_value",
            "station_value",
            "time_difference(minutes)"
        ])

        for img in tqdm.tqdm(FY3DImage.all_images()):

            # Получаем площадку станции на снимке
            img_sites_names = get_areas.get_image_sites(img)

            for site_name in img_sites_names:
                lat, lon = sites.get_site_pos(site_name)
                area = get_areas.get_site_area(img, lat, lon)
                satellite_ref_value = process_areas.calculate_area_value(area, channel)

                # Получаем данные со станции
                site_value = process_areas.calculate_site_value(img, channel, site_name)

                site_data = sites.get_image_site_data(site_name, img)
                sat_dt = img.get_datetime()
                site_dt = site_data["Datetime"]
                time_diff = abs(sat_dt - site_dt)
                time_diff_minutes = time_diff.total_seconds() // 60

                if time_diff_minutes > 360:
                    continue

                print(channel, area.image.id, area.x, area.y)
                df.loc[len(df)] = [
                    img.id,
                    site_name,
                    satellite_ref_value,
                    site_value,
                    time_diff_minutes
                ]

        df.to_excel(writer, sheet_name=f"Канал {channel}", index=False)
