import numpy as np
import pandas as pd

import os
from time import time as t


def lower_station_name(station):
    return station.lower().replace("'", "_").replace("-", "_").replace(" ", "_")


def np_datetime2y_m_d_h_m(date, config):

    date = pd.to_datetime(date)
    config["_year"] = date.year
    config["_month"] = date.month
    config["_day"] = date.day
    config["_hour"] = date.hour
    config["_minute"] = date.minute

    return config


def reconstruct_datetime(prm):
    date = prm["_year"] + '-' + prm["_month"] + '-' + prm["_month"] + '-' + prm["_day"] + '_' + prm["_hour"]
    return date


def detect_existing_case(index, path):
    if index > 0:
        for element in os.listdir(path):
            if "NINJAFOAM" in element:
                return element
        return None


def print_current_prediction(time, speed, direction, temp, cc, speed_pred, ang_pred):
    print(f"\n Time: {time} "
          f"\n AROME speed: {speed}"
          f"\n AROME direction: {direction}"
          f"\n AROME temperature: {temp}"
          f"\n AROME cloud cover: {cc}"
          f"\n WindNinja speed: {speed_pred}"
          f"\n WindNinja direction: {ang_pred}\n")


def print_begin_end(begin, end):
    print('\n\n__________________________')
    print('__________________________\n')
    print(f'_______{begin}___________\n')
    print(f'_______{end}___________\n')
    print('__________________________')
    print('__________________________\n\n')


def print_with_frame(text):
    print('\n\n__________________________')
    print('__________________________\n')
    print(f'_______{text}_______\n')
    print('__________________________')
    print('__________________________\n\n')


def print_date(year, month, day, hour, minute):
    print('\n\n__________________________')
    print(f'Year:{year}_________________\n')
    print(f'Month:{month}_________________\n')
    print(f'Day:{day}_________________\n')
    print(f'Hour:{hour}_________________\n')
    print(f'Minute:{minute}_________________\n')
    print('__________________________\n\n')


def timer_decorator(apply_timer=True, argument="", unit='minute', level="__"):
    def decorator(function):
        def wrapper(*args, **kwargs):
            if apply_timer:
                t0 = t()

            result = function(*args, **kwargs)

            if apply_timer:
                t1 = t()
                if unit == "hour":
                    time_execution = np.round((t1 - t0) / 3600, 2)
                elif unit == "minute":
                    time_execution = np.round((t1 - t0) / 60, 2)
                elif unit == "second":
                    time_execution = np.round((t1 - t0), 2)
                print(f"{level}Time to calculate {argument}: {time_execution} {unit}s")
            return result
        return wrapper
    return decorator
