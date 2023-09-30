from database import *
from FY3DImage import FY3DImage
from FY3DImageArea import FY3DImageArea
from vars import KMirrorSide, SurfaceType
import pandas as pd
from functools import reduce


class Deviations(BaseModel):
    area = ForeignKeyField(FY3DImageArea, backref="deviations")
    channel = IntegerField()
    sensor = IntegerField()
    deviation = FloatField()
    area_avg = FloatField()

    @classmethod
    def get_dataframe(cls,
                      k_mirror_side: KMirrorSide = None,
                      surface_type: SurfaceType = None,
                      year: int = None,
                      channel: int = None,
                      sensor: int = None) -> pd.DataFrame:
        expressions = []
        if k_mirror_side is not None:
            expressions.append(FY3DImageArea.k_mirror_side == k_mirror_side.value)
        if surface_type is not None:
            expressions.append(FY3DImageArea.surface_type == surface_type.value)
        if year is not None:
            expressions.append(FY3DImage.year == year)
        if channel is not None:
            expressions.append(Deviations.channel == channel)
        if sensor is not None:
            expressions.append(Deviations.sensor == sensor)
        filt = reduce(lambda x, y: x & y, expressions)
        result = Deviations.select(FY3DImage.year,
                                   Deviations.channel, Deviations.sensor, Deviations.deviation, Deviations.area_avg,
                                   FY3DImageArea.surface_type, FY3DImageArea.k_mirror_side) \
            .join(FY3DImageArea) \
            .join(FY3DImage) \
            .where(filt)
        df = pd.DataFrame(list(result.dicts()))
        return df


Deviations.create_table()