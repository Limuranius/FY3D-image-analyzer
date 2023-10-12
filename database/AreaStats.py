import pandas as pd

from .BaseModel import *
from .FY3DImageArea import FY3DImageArea
from .FY3DImage import FY3DImage
from vars import SurfaceType
from functools import reduce


class AreaStats(BaseModel):
    area = ForeignKeyField(FY3DImageArea, backref="stats")
    channel = IntegerField()
    area_avg = FloatField()
    area_std = FloatField()

    @classmethod
    def get_dataframe(cls,
                      surface_type: SurfaceType = None,
                      year: int = None,
                      channel: int = None) -> pd.DataFrame:
        expressions = [
            FY3DImage.is_selected == True,
            FY3DImageArea.is_selected == True
        ]
        if surface_type is not None:
            expressions.append(FY3DImageArea.surface_type == surface_type.value)
        if year is not None:
            expressions.append(FY3DImage.year == year)
        if channel is not None:
            expressions.append(AreaStats.channel == channel)
        filt = reduce(lambda x, y: x & y, expressions)
        result = AreaStats.select(FY3DImage.year,
                                  AreaStats.channel, AreaStats.area_avg, AreaStats.area_std,
                                  FY3DImageArea.surface_type, FY3DImageArea.k_mirror_side) \
            .join(FY3DImageArea) \
            .join(FY3DImage) \
            .where(filt)
        df = pd.DataFrame(list(result.dicts()))
        return df


AreaStats.create_table()
