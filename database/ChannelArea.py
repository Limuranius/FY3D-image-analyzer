from __future__ import annotations
import numpy as np
from utils import area_utils
from vars import KMirrorSide, SurfaceType


class ChannelArea:
    __ch_area: np.ndarray

    parent: "FY3DImageArea"
    channel: int
    sea_value: int
    ice_value: int
    sea_mask: np.ndarray
    true_noise: np.ndarray
    median_values: np.ndarray
    h: int
    w: int

    @classmethod
    def from_ndarray(cls, ch_area: np.ndarray, channel: int) -> ChannelArea:
        return ChannelArea(
            ch_area=ch_area,
            channel=channel,
        )

    @classmethod
    def from_area(cls, area: "FY3DImageArea", channel: int) -> ChannelArea:
        return ChannelArea(
            ch_area=area.get_vis_channel(channel).astype(np.int32),
            channel=channel,
            parent=area,
        )

    def __init__(self,
                 ch_area: np.ndarray,
                 channel: int,
                 parent: "FY3DImageArea" = None,
                 ):
        self.parent = parent
        self.__ch_area = ch_area
        self.channel = channel
        self.h, self.w = self.__ch_area.shape
        self.sea_mask = area_utils.ch_area_to_sea_mask(self.__ch_area)
        self.sea_value, self.ice_value = area_utils.find_two_peaks(self.__ch_area)

        self.true_noise = self.to_numpy().copy()
        self.true_noise[self.sea_mask] -= self.sea_value
        self.true_noise[~self.sea_mask] -= self.ice_value

        self.median_values = self.to_numpy().copy()
        self.median_values[self.sea_mask] = self.sea_value
        self.median_values[~self.sea_mask] = self.ice_value

    def to_numpy(self) -> np.ndarray:
        return self.__ch_area

    def unique_str(self) -> str:
        return f"{self.parent.id}_{self.channel}"

    @classmethod
    def find(cls,
             channel: int,
             k_mirror_side: KMirrorSide = None,
             surface_type: SurfaceType = None,
             year: int = None):
        from database import FY3DImageArea
        from tqdm import tqdm
        areas = FY3DImageArea.find(
            k_mirror_side=k_mirror_side,
            surface_type=surface_type,
            year=year
        )
        res = []
        for area in tqdm(areas):
            res.append(area.get_channel_area(channel))
        return res
