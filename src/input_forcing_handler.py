import numpy as np
import pandas as pd

from abc import ABC, abstractmethod

from src.grid_utils import project_coordinates


class NWPDataHandler(ABC):

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def get_temperature(self, station):
        pass

    @abstractmethod
    def get_cloud_cover(self, station):
        pass

    @abstractmethod
    def get_wind_speed(self, station):
        pass

    @abstractmethod
    def get_wind_direction(self, station):
        pass

    @abstractmethod
    def get_x_y_station(self, station):
        pass

    @abstractmethod
    def get_lat_lon_station(self, station):
        pass

    @abstractmethod
    def get_time(self, station):
        pass


def df_select_date(df, begin, end):
    begin = pd.to_datetime(begin, format='%Y-%m-%d-%H')
    end = pd.to_datetime(end, format='%Y-%m-%d-%H')
    return df.sort_index().loc[begin:end]


def df_select_station(df, station):
    return df[df["name"] == station]


class PKLHandler(NWPDataHandler):

    def __init__(self, config):
        self.config = config
        self.df = None
        self.data_is_loaded = False

    def load_data(self):
        self.df = pd.read_pickle(self.config["path_to_nwp"])
        self.df.index = pd.to_datetime(self.df.index)
        self.data_is_loaded = True

    def preprocess(self):

        assert self.data_is_loaded, "Data must be loaded before with load_data method"

        if self.config["apply_qc"]:
            self.df = self.df.loc[:, self.df["qc"] == 1]
        self.df = df_select_date(self.df, self.config["begin"], self.config["end"])

    def get_temperature(self, station=None):
        df = self.df if station is None else df_select_station(self.df, station)
        return np.round(df[self.config["temperature_name"]].values)

    def get_cloud_cover(self, station=None):
        df = self.df if station is None else df_select_station(self.df, station)
        return np.round(df[self.config["cloud_cover_name"]].values)

    def get_wind_speed(self, station=None):
        df = self.df if station is None else df_select_station(self.df, station)
        # Wind Ninja only accepts rounded values for input winds
        return np.round(df[self.config["wind_speed_name"]].values)

    def get_wind_direction(self, station=None):
        df = self.df if station is None else df_select_station(self.df, station)
        return np.round(df[self.config["wind_direction_name"]].values)

    def get_x_y_station(self, station):
        df = df_select_station(self.df, station)
        if 'x' not in df or 'y' not in df:
            lat, lon = self.get_lat_lon_station(station)
            return project_coordinates(lon=lon,
                                       lat=lat,
                                       crs_in=self.config["crs_in"],
                                       crs_out=self.config["crs_out"])
        return df.loc[df["name"] == station, ["x", "y"]].values

    def get_lat_lon_station(self, station):
        df = df_select_station(self.df, station)
        return df.loc[df["name"] == station, ["lat", "lon"]].iloc[0].values

    def get_time(self, station):
        return self.df.loc[self.df["name"] == station, :].index.values
