import numpy as np
import pandas as pd

import os
import shutil
from dataclasses import dataclass
from typing import Union

from src.utils_wind_ninja import lower_station_name, detect_existing_case, print_date
from src.utils_wind_ninja import print_current_prediction


def delete_temporary_files(prm):
    for path in [prm["tmp"], prm["output_path"]]:
        for item in os.listdir(path):
            if item.endswith(".asc") or item.endswith(".nc") or item.endswith(".kmz") or item.endswith(".prj"):
                os.remove(os.path.join(path, item))
                print(f"removed {os.path.join(path, item)}")


@dataclass
class TemporaryMeteo:
    speed: float
    direction: float
    temperature: float
    cc: float


@dataclass
class TemporaryTime:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    time: np.datetime64


@dataclass
class TemporaryPrediction:
    speed_pred: float
    ang_pred: float


class TemporaryData:

    def __init__(self, station, config):
        self.config: dict = config
        self.station_lower: str = lower_station_name(station)

        self.tmp_time: Union[TemporaryTime, None] = None
        self.current_time_is_set: bool = False
        self.tmp_meteo: Union[TemporaryMeteo, None] = None
        self.current_meteo_is_set: bool = False
        self.tmp_pred: Union[TemporaryPrediction, None] = None
        self.current_prediction_is_set = False

    def get_dem_name(self):
        return self.config["tmp"] + f"{self.station_lower}_2km.tif"

    def set_current_time(self, time):
        time = pd.to_datetime(time)

        self.tmp_time = TemporaryTime(time.year, time.month, time.day, time.hour, time.minute, time)
        self.current_time_is_set = True
        print_date(*self.get_split_time())

    def get_split_time(self):
        return self.tmp_time.year, self.tmp_time.month, self.tmp_time.day, self.tmp_time.hour, self.tmp_time.minute

    def delete_ninjafoam_folder(self, index):
        case = detect_existing_case(index, self.config["tmp"])
        shutil.rmtree(self.config["tmp"]+case)
        print(f"removed folder {self.config['tmp']+case}")

    def set_tmp_meteo_data(self, speed, direction, temperature, cc):
        self.tmp_meteo = TemporaryMeteo(speed, direction, temperature, cc)

    def set_tmp_pred(self, speed_pred, ang_pred):
        self.tmp_pred = TemporaryPrediction(speed_pred, ang_pred)

    def print_current_tmp_data(self):
        print_current_prediction(self.tmp_time.time,
                                 self.tmp_meteo.speed,
                                 self.tmp_meteo.direction,
                                 self.tmp_meteo.temperature,
                                 self.tmp_meteo.cc,
                                 self.tmp_pred.speed_pred,
                                 self.tmp_pred.ang_pred)

    def clean(self):
        delete_temporary_files(self.config)
        self.tmp_time = None
        self.current_time_is_set = False
        self.tmp_meteo = None
        self.current_meteo_is_set = False
        self.tmp_pred = None
        self.current_prediction_is_set = False
