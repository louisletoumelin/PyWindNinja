def select_cfg_file(config):
    path_to_wn = config["working_directory"] + "cfg/"
    wn_options = {"momentum": path_to_wn + "cli_momentumSolver_diurnal.cfg",
                  "mass": path_to_wn + "mass_conserving.cfg"}
    config["cfg_file"] = wn_options[config["solver"]]
    return config


def create_begin_end(config):
    config["begin"] = f"{config['year_begin']}-{config['month_begin']}-{config['day_begin']}-{config['hour_begin']}"
    config["end"] = f"{config['year_end']}-{config['month_end']}-{config['day_end']}-{config['hour_end']}"
    return config
