import datetime
import pandas as pd
import load_files
import all_the_math


def get_closest_value(target: int | float, values: list[int | float]):
    min_delta = abs(target - values[0])
    closest = values[0]
    for value in values:
        delta = abs(value - closest)
        if delta < min_delta:
            closest = value
            min_delta = delta
    return closest


def get_closest_date_data(df: pd.DataFrame, site: str, dt: datetime.datetime):
    site_data = df[df["Site"] == site]
    i = abs(site_data["Datetime"] - dt).argmin()
    row = site_data.loc[i]

    max_time_diff = datetime.timedelta(hours=3)
    assert abs(row["Datetime"] - dt) < max_time_diff
    return row


def get_site_Ltoa(
        df_ocean_color: pd.DataFrame,
        df_aerosol_phase: pd.DataFrame,
        df_aerosol: pd.DataFrame,
        site: str,
        dt: datetime.datetime,
        wavelength: float,
):
    ocean_color = get_closest_date_data(df_ocean_color, site, dt)
    aerosol_phase = get_closest_date_data(df_aerosol_phase, site, dt)
    aerosol = get_closest_date_data(df_aerosol, site, dt)

    closest_wl = get_closest_value(
        wavelength,
        [412, 440, 443, 490, 500, 510, 531, 532, 551, 555, 560, 620, 667, 675, 681, 709, 779, 865, 870, 1020]
    )

    closest_wl_2 = get_closest_value(
        wavelength,
        [440, 675, 870, 1020]
    )

    ROT = ocean_color[f"Rayleigh_Optical_Depth[{closest_wl}nm]"]
    AOT = ocean_color[f"Aerosol_Optical_Depth[{closest_wl}nm]"]
    OOT = ocean_color[f"Ozone_Optical_Depth[{closest_wl}nm]"]
    LwnfQ = ocean_color[f"Lwn_f/Q[{closest_wl}nm]"]
    SSA = aerosol[f"Single_Scattering_Albedo[{closest_wl_2}nm]"]

    return all_the_math.L_toa(
        wavelength,
        solar_zenith=...,
        sat_zenith=...,
        delta_azimuth=...,
        ROT=ROT,
        SSA=SSA,
        AOT=AOT,
        OOT=OOT,
        LwnfQ=LwnfQ
    )


df_aerosol = load_files.load_no_phase()
df_aerosol_phase = load_files.load_phase()
df_ocean_color = load_files.load_ocean_color()
