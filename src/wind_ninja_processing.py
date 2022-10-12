import numpy as np
import xarray as xr
from osgeo import gdal
import os
import shutil

from WindNinja_learning.grid_utils import find_nearest_neighbor_in_grid
from WindNinja_learning.utils_wind_ninja import detect_existing_case, timer_decorator
from WindNinja_learning.config import config


def launch_wind_ninja_experiment(index, tmp_data, config):
    # Launch windninja simulation
    exp = f"{config['cfg_file']}  " \
          f"--elevation_file {tmp_data.get_dem_name()} " \
          f"--input_speed {tmp_data.tmp_meteo.speed} " \
          f"--input_direction {tmp_data.tmp_meteo.direction} " \
          f"--mesh_resolution 30 " \
          f"--units_mesh_resolution m " \
          f"--uni_air_temp {tmp_data.tmp_meteo.temperature} " \
          f"--uni_cloud_cover {tmp_data.tmp_meteo.cc} " \
          f"--year {tmp_data.tmp_time.year} " \
          f"--month {tmp_data.tmp_time.month} " \
          f"--day {tmp_data.tmp_time.day} " \
          f"--hour {tmp_data.tmp_time.hour} " \
          f"--minute {tmp_data.tmp_time.minute} " \
          f"--output_path {config['output_path']}"

    # Use existing case if it exists
    case = detect_existing_case(index, config["tmp"])

    if case is not None:
        print(f"launch_wind_ninja_experiment: case is {case}")
        exp = f"{config['cfg_file']}  " \
              f"--elevation_file {tmp_data.get_dem_name()} " \
              f"--existing_case_directory {config['tmp'] + case} " \
              f"--input_speed {tmp_data.tmp_meteo.speed} " \
              f"--input_direction {tmp_data.tmp_meteo.direction} " \
              f"--uni_air_temp {tmp_data.tmp_meteo.temperature} " \
              f"--uni_cloud_cover {tmp_data.tmp_meteo.cc} " \
              f"--year {tmp_data.tmp_time.year} " \
              f"--month {tmp_data.tmp_time.month} " \
              f"--day {tmp_data.tmp_time.day} " \
              f"--hour {tmp_data.tmp_time.hour} " \
              f"--minute {tmp_data.tmp_time.minute} " \
              f"--output_path {config['output_path']}"
    else:
        print("launch_wind_ninja_experiment: case is None")

    # Launch experience
    os.system(config["path_to_WindNinja"] + "WindNinja_cli " + exp)


def _float_to_string_for_dates(day_float):
    day_str = f"0{str(day_float)}" if day_float < 10 else str(day_float)
    return day_str


def _create_filename(path, filename, format_file):
    name_speed = f"{path}{filename}_vel.{format_file}"
    name_ang = f"{path}{filename}_ang.{format_file}"
    return name_speed, name_ang


def asc_to_netcdf(tmp_data, config):
    # Convert outputs from .asc to netcdf
    dates = tmp_data.get_split_time()
    year_str, month_str, day_str, hour_str, min_str = [_float_to_string_for_dates(date) for date in dates]

    # Convert the predictions to netcdf
    speed = np.intp(tmp_data.tmp_meteo.speed)
    direction = np.intp(tmp_data.tmp_meteo.direction)
    output_str = f"{tmp_data.station_lower}_2km_{direction}_{speed}_{month_str}-{day_str}-{year_str}_{hour_str}{min_str}_30m"
    name_speed_asc, name_ang_asc = _create_filename(config['tmp'], output_str, "asc")
    name_speed_nc, name_ang_nc = _create_filename(config['output_path'], output_str, "nc")

    gdal.Translate(name_speed_nc, name_speed_asc)
    gdal.Translate(name_ang_nc, name_ang_asc)

    return name_speed_nc, name_ang_nc


def extract_nearest_neighbor(speed_pred, ang_pred, x_l93, y_l93):
    # Select the nearest neighbor to the station
    index_nearest_neighbor = find_nearest_neighbor_in_grid(speed_pred.x.values,
                                                           speed_pred.y.values,
                                                           [(x_l93, y_l93)],
                                                           number_of_neighbors=1)
    x_idx = np.intp(index_nearest_neighbor[0])
    y_idx = np.intp(index_nearest_neighbor[1])

    speed_pred = speed_pred.isel(x=x_idx, y=y_idx).values
    ang_pred = ang_pred.isel(x=x_idx, y=y_idx).values

    return speed_pred, ang_pred


@timer_decorator(apply_timer=config["apply_timer"], argument="windninja2nc", unit='second', level="__")
def windninja2nc(index, tmp_data, config):
    try:
        launch_wind_ninja_experiment(index, tmp_data, config)
        print("WindNinja launched without error")
    except ValueError:
        print("\nValueError encountered."
              "\nTrying to relaunch simulation without using existing case\n")
        case = detect_existing_case(index,
                                    config["tmp"])
        if case is not None:
            shutil.rmtree(config["tmp"] + case,
                          ignore_errors=True)
            launch_wind_ninja_experiment(0, tmp_data, config)
        else:
            raise
    name_speed_nc, name_ang_nc = asc_to_netcdf(tmp_data,
                                               config)
    return name_speed_nc, name_ang_nc
