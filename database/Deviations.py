from .BaseModel import *
from .FY3DImage import FY3DImage
from .FY3DImageArea import FY3DImageArea
from .AreaStats import AreaStats
from vars import KMirrorSide, SurfaceType
import pandas as pd
from functools import reduce

_deviations_df: pd.DataFrame = None


class Deviations(BaseModel):
    area = ForeignKeyField(FY3DImageArea, backref="deviations")
    channel = IntegerField()
    sensor = IntegerField()
    deviation = FloatField()
    sensor_avg = FloatField()

    @classmethod
    def __load_df(cls):
        global _deviations_df
        _deviations_df = pd.DataFrame(
            Deviations.select(FY3DImage.year, FY3DImage.is_selected,
                              Deviations.channel, Deviations.sensor, Deviations.deviation,
                              AreaStats.area_avg, AreaStats.area_std,
                              FY3DImageArea.surface_type, FY3DImageArea.k_mirror_side)
                .join(FY3DImageArea)
                .join(AreaStats, on=(AreaStats.area == FY3DImageArea.id) & (AreaStats.channel == Deviations.channel))
                .switch(FY3DImageArea)
                .join(FY3DImage).dicts()
        )

    @classmethod
    def get_dataframe(cls,
                      k_mirror_side: KMirrorSide = None,
                      surface_type: SurfaceType = None,
                      year: int = None,
                      channel: int = None,
                      sensor: int = None,
                      check_select: bool = True) -> pd.DataFrame:
        global _deviations_df
        if _deviations_df is None:
            cls.__load_df()
        expressions = []
        if check_select:
            expressions.append(_deviations_df.is_selected == True)
        if k_mirror_side is not None:
            expressions.append(_deviations_df.k_mirror_side == k_mirror_side.value)
        if surface_type is not None:
            expressions.append(_deviations_df.surface_type == surface_type.value)
        if year is not None:
            expressions.append(_deviations_df.year == year)
        if channel is not None:
            expressions.append(_deviations_df.channel == channel)
        if sensor is not None:
            expressions.append(_deviations_df.sensor == sensor)
        if expressions:
            filt = reduce(lambda x, y: x & y, expressions)
            result = _deviations_df[filt]
        else:
            result = _deviations_df
        return result

    @classmethod
    def get_count(cls,
                  k_mirror_side: KMirrorSide = None,
                  surface_type: SurfaceType = None,
                  year: int = None,
                  channel: int = None,
                  sensor: int = None,
                  check_select: bool = True) -> int:
        result = cls.get_dataframe(k_mirror_side, surface_type, year, channel, sensor, check_select)
        return len(result)


Deviations.create_table()
