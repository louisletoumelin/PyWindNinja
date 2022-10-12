import matplotlib.pyplot as plt

from time import time as t

from src.config import config
from src.input_forcing_handler import PKLHandler
from src.grid_utils import crop_and_save_dem
from src.wind_ninja_processing import windninja2nc
from src.temporary_data import TemporaryData
from src.result import ResultHandler

"""
momentum:
06/10/202 - 7 minutes for 24 time steps at one station (domain 2km x 2km) (43 hours for one year at one station)

mass:
06/10/2022 - 29 seconds for 24 time steps at one station (domain 2km x 2km)  (2h53min for one year at one station)
06/10/2022 - 29 minutes for one month (January 2019) at one station (domain 2km x 2km)
"""

data_handler = PKLHandler(config)
data_handler.load_data()
data_handler.preprocess()

# todo write a CSVHandler
# todo write a netcdf Handler
# todo select DataHandler

results_handler = ResultHandler(config)

t0 = t()

for station in config["stations"]:

    # Get input data
    cloud_covers = data_handler.get_cloud_cover(station)
    temperatures = data_handler.get_temperature(station)
    wind_speeds = data_handler.get_wind_speed(station)
    wind_directions = data_handler.get_wind_direction(station)
    x_l93, y_l93 = data_handler.get_x_y_station(station)
    times = data_handler.get_time(station)

    # Initialize temporary data handler
    tmp_data = TemporaryData(station, config)

    # Select area of interest
    crop_and_save_dem(x_l93 - config["dx"],
                      y_l93 + config["dy"],
                      x_l93 + config["dx"],
                      y_l93 - config["dy"],
                      input_topo=config["topo_path"],
                      output_topo=tmp_data.get_dem_name()
                      )

    # Each time step are downscaled sequentially
    for index, (time, speed) in enumerate(zip(times, wind_speeds)):

        tmp_data.set_current_time(time)

        if speed > 0:

            tmp_data.set_tmp_meteo_data(speed, wind_directions[index], temperatures[index], cloud_covers[index])

            # Launch WindNinja
            name_speed_nc, name_dir_nc = windninja2nc(index, tmp_data, config)

            # Extract values from prediction
            speed_pred, ang_pred = results_handler.extract_value_from_nc(name_speed_nc, name_dir_nc, x_l93, y_l93)

            tmp_data.set_tmp_pred(speed_pred, ang_pred)
        else:
            print(f"\n\nSpeed=0 at time {time}\n\n")

            # If large scale speed is null, downscaled speed is null
            tmp_data.set_tmp_meteo_data(0, 0, temperatures[index], cloud_covers[index])
            tmp_data.set_tmp_pred(0, 0)

        # Extract results
        results_handler.set_results_at_center(station, time, tmp_data)

        # Print current results
        tmp_data.print_current_tmp_data()
        tmp_data.clean()

    results_handler.set_df_results(station)

    # Clean ninjafoam folders
    if config["solver"] == "momentum":
        tmp_data.delete_ninjafoam_folder(index)

    print(f"\n{(t() - t0) / 60} minutes to predict all time steps")

results_handler.save_df_results()
results_handler.save_config()

plt.figure()
ax = plt.gca()
results_handler.results_df["Col du Lac Blanc"]["UV_wn"].plot(ax=ax, label="Wind Ninja")
data_handler.df["Wind"][data_handler.df["name"] == "Col du Lac Blanc"].plot(ax=ax, label="AROME")
data_handler.df["vw10m(m/s)"][data_handler.df["name"] == "Col du Lac Blanc"].plot(ax=ax, label="observation")
plt.legend()

