from pyorbital import tlefile
from pyorbital.orbital import Orbital
from pyorbital import astronomy
from datetime import datetime, timedelta


MIN_ELEVATION = 70


def get_sea_sites():
    path = "sea_sites.txt"
    with open(path) as f:
        return f.read().split()


def get_sites_coords():
    path = "aeronet_locations.txt"
    sites_coords = dict()
    with open(path) as f:
        f.readline()
        f.readline()
        for line in f.readlines():
            line = line.strip()
            name, lon, lat, alt = line.split(",")
            sites_coords[name] = (float(lon), float(lat), float(alt))
    return sites_coords


sites_coords = get_sites_coords()
sea_sites = get_sea_sites()

SATELLITE = "FY-3D"
TLE_PATH = "TLE-FY3D-03-06-23.txt"


class OrbitPredictor:
    def __init__(self):
        self.orbit = Orbital(SATELLITE, tle_file=TLE_PATH)

    def get_coords(self, dt: datetime):
        return self.orbit.get_lonlatalt(dt)

    def get_angles_for_sea_sites(self, dt: datetime):
        res = []
        for site in sea_sites:
            lon, lat, alt = sites_coords[site]
            azimuth, elevation = self.orbit.get_observer_look(dt, lon, lat, alt)
            res.append((azimuth, elevation, site))
        return res

    def is_night_side(self, dt: datetime) -> bool:
        lon, lat, alt = self.get_coords(dt)
        angle = astronomy.sun_zenith_angle(dt, lon, lat)
        return angle > 90

    def get_optimal_sea_sites(self, dt: datetime):
        angles = self.get_angles_for_sea_sites(dt)
        res = []
        for azimuth, elevation, site in angles:
            if elevation > MIN_ELEVATION:
                res.append((azimuth, elevation, site))
        return res

    #
    # def is_point_visible(self, lon, lat, alt, dt: datetime) -> bool:
    #     self.orbit.get_next_passes()


def main():
    # o = OrbitPredictor()
    # start = datetime(2023, 6, 1)
    # step = timedelta(minutes=5)
    # for i in range(100):
    #     t = start + step * i
    #     if not o.is_night_side(t):
    #         print(t, o.get_optimal_sea_sites(t))

    o = OrbitPredictor()
    start = datetime(2023, 12, 3)
    lon, lat, alt = 131.8971482141884, 43.03237160140015, 0
    HOURS = 24
    res = o.orbit.get_next_passes(start, HOURS, lon, lat, alt)
    for t in res:
        mid_time = t[2]
        print(mid_time)

main()
