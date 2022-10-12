from utils_config import select_cfg_file, create_begin_end

config = {}
config["exp_name"] = "test"
config["stations"] = ["Col du Lac Blanc", 'LES ROCHILLES-NIVOSE']

# 2 August 2017 1h
config["hour_begin"] = 0
config["day_begin"] = 1
config["month_begin"] = 11
config["year_begin"] = 2019

# 31 May 2020 1h
config["hour_end"] = 3
config["day_end"] = 1
config["month_end"] = 11
config["year_end"] = 2019

# General
config["apply_qc"] = False
config["temperature_name"] = 'Tair'
config["cloud_cover_name"] = 'CC_cumul'
config["wind_speed_name"] = 'Wind'
config["wind_direction_name"] = 'Wind_DIR'
config["dx"] = 1_000
config["dy"] = 1_000
config["apply_timer"] = True
config["crs_in"] = 4326
config["crs_out"] = 2154

# General Wind Ninja
config["solver"] = "mass"  # "momentum" or "mass"

# Parent directory
config["working_directory"] = 'C:/Users/louis/git/PyWindNinja/'

# Data
config["path_to_nwp"] = config["working_directory"] + 'Data/Inputs/time_series_bc.pkl'
config["output_path"] = config["working_directory"] + "Data/Outputs/"

# Topography
config["topo_path"] = config["working_directory"] + "Data/Inputs/COP30_L93_cropped.tif"
config['tmp'] = config["working_directory"] + "Data/tmp/"

# WindNinja
config["path_to_WindNinja"] = "C:/WindNinja/WindNinja-3.7.2/bin/"

config = select_cfg_file(config)
config = create_begin_end(config)
