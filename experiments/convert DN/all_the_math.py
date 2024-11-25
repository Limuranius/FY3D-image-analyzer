import datetime
from math import cos, sin, acos, tan, exp, pi


def get_solar_irradiance(wavelength: float) -> float:
    pass


def dt_to_jday(dt: datetime.datetime) -> float:
    pass


def P_r(theta: float):
    return 0.75 * (1 + cos(theta) ** 2)


def r(theta: float):
    theta_t = 1 / sin(1.34 * sin(theta))
    return 0.5 * (
        sin(theta - theta_t) ** 2 / sin(theta + theta_t) ** 2 +
        tan(theta - theta_t) ** 2 / tan(theta + theta_t) ** 2
    )


def p_r(solar_zenith: float,
        sat_zenith: float,
        delta_azimuth: float, ):
    theta_plus = acos(cos(solar_zenith) * cos(sat_zenith) - sin(solar_zenith) * sin(sat_zenith) * cos(delta_azimuth))
    theta_minus = acos(-cos(solar_zenith) * cos(sat_zenith) - sin(solar_zenith) * sin(sat_zenith) * cos(delta_azimuth))
    return P_r(theta_minus) + (r(sat_zenith) + r(solar_zenith)) * P_r(theta_plus)


def L_toa(
        wavelength: float,
        solar_zenith: float,
        sat_zenith: float,
        delta_azimuth: float,
        ROT: float,
        SSA: float,
        AOT: float,
        OOT: float,
        LwnfQ: float
):
    rho_r = ROT * p_r(solar_zenith, sat_zenith, delta_azimuth) / (4 * cos(solar_zenith) * cos(sat_zenith))
    theta_minus = acos(-cos(solar_zenith) * cos(sat_zenith) - sin(solar_zenith) * sin(sat_zenith) * cos(delta_azimuth))
    rho_a = SSA * AOT * P_a(theta_minus) / (4 * cos(solar_zenith) * cos(sat_zenith))
    t0 = exp(-(ROT / 2 + OOT) / cos(solar_zenith))
    tv = exp(-(ROT / 2 + OOT) / cos(sat_zenith))
    rho_w = LwnfQ * 10 * pi / get_solar_irradiance(wavelength)

    rho_toa = rho_r + rho_a + t0 * tv * rho_w

    return rho_toa * get_solar_irradiance(wavelength) * cos(solar_zenith) / (pi * d ** 2)