import numpy as np
import pandas as pd
import xarray as xr

from collections import defaultdict, deque
import uuid
import pickle
import json
from pathlib import Path

from src.wind_ninja_processing import extract_nearest_neighbor
from src.utils_wind_ninja import timer_decorator
from config import config


def read_nc_output(filename):
    return xr.open_dataset(filename).Band1


class ResultHandler:

    def __init__(self, config):
        self.config = config
        self.results_at_center = defaultdict(lambda: defaultdict(deque))
        self.results_df = dict()
        self.uuid_str = str(uuid.uuid4())[:4]

        self.path_to_experience_folder = self.config["output_path"] + self.uuid_str
        self.create_experience_folder()

    def create_experience_folder(self):
        Path(self.path_to_experience_folder).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_speed_and_angle_prediction(name_speed_nc, name_direction_nc):
        return read_nc_output(name_speed_nc), read_nc_output(name_direction_nc)

    def extract_value_from_nc(self, name_speed_nc, name_direction_nc, x_l93, y_l93):
        speed_nc, direction_nc = self.read_speed_and_angle_prediction(name_speed_nc, name_direction_nc)
        speed_pred, ang_pred = extract_nearest_neighbor(speed_nc, direction_nc, x_l93, y_l93)
        return speed_pred, ang_pred

    @timer_decorator(apply_timer=config["apply_timer"], argument="set_results_at_center", unit='second', level="__")
    def set_results_at_center(self, station, time, tmp_data):
        self.results_at_center[station]["wn_speed"].append(tmp_data.tmp_pred.speed_pred)
        self.results_at_center[station]["time"].append(time)
        self.results_at_center[station]["wn_direction"].append(tmp_data.tmp_pred.ang_pred)

    def get_last_speed_prediction(self, station):
        return self.results_at_center[station]["wn_speed"][-1]

    def get_last_direction_prediction(self, station):
        return self.results_at_center[station]["wn_direction"][-1]

    def get_last_time_prediction(self, station):
        return self.results_at_center[station]["time"][-1]

    @timer_decorator(apply_timer=config["apply_timer"], argument="set_df_results", unit='second', level="__")
    def set_df_results(self, station):
        array_speeds = self.results_at_center[station]["wn_speed"]
        array_directions = self.results_at_center[station]["wn_direction"]
        times_predictions = self.results_at_center[station]["time"]
        np_results = np.transpose([array_speeds, array_directions])
        self.results_df[station] = pd.DataFrame(np_results,
                                                columns=["UV_wn", "UV_DIR_wn"],
                                                index=times_predictions)
        print("WindNinja: results are set")

    @timer_decorator(apply_timer=config["apply_timer"], argument="save_df_results", unit='second', level="__")
    def save_df_results(self):
        name = self.config["exp_name"] + '_' + self.uuid_str
        path = Path(self.path_to_experience_folder) / (name + '.pickle')
        with path.open('wb') as handle:
            pickle.dump(self.results_df, handle)
        print(f"Saving results at {path}")

    def save_config(self):
        name = self.config["exp_name"] + "_config_" + self.uuid_str
        path = Path(self.path_to_experience_folder) / (name + '.json')
        with path.open("w") as fp:
            json.dump(self.config, fp, sort_keys=True, indent=4)
        print(f"Saving config at {path}")

