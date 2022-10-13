import numpy as np
import pyproj
from scipy.spatial import cKDTree
import os
os.environ['USE_PATH_FOR_GDAL_PYTHON'] = 'YES'
from osgeo import gdal
import concurrent.futures

from src.utils_wind_ninja import timer_decorator
from config import config


def project_coordinates(lon=None, lat=None, crs_in=4326, crs_out=2154):

    gps_to_l93_func = pyproj.Transformer.from_crs(crs_in, crs_out, always_xy=True)
    projected_points = [point for point in gps_to_l93_func.itransform([(lon, lat)])][0]
    return projected_points


@timer_decorator(apply_timer=config["apply_timer"], argument="crop_and_save_dem", unit='second', level="__")
def crop_and_save_dem(x_min,
                      y_max,
                      x_max,
                      y_min,
                      input_topo='C:/path/to/file/COP30_L93_cropped.tif',
                      output_topo='C:/path/to/folder/'):

    bbox = (x_min, y_max, x_max, y_min)
    ds = gdal.Open(input_topo)
    gdal.Translate(output_topo, ds, projWin=bbox)
    #os.system("gdal_translate -of GTiff " + input_topo + " " + output_topo)
    """
    from rasterio.windows import from_bounds
    with rasterio.open(config["topo_path"]) as src:
        rst = src.read(1, window=from_bounds(943565, 6451415, 945567, 6453414, src.transform))
    """


def x_y_to_stacked_xy(x_array, y_array):
    stacked_xy = np.dstack((x_array, y_array))
    return stacked_xy


def grid_to_flat(stacked_xy):
    x_y_flat = [tuple(i) for line in stacked_xy for i in line]
    return x_y_flat


def find_nearest_neighbor_in_grid(x_grid, y_grid, list_coord_station, number_of_neighbors=1):

    def K_N_N_point(point):
        distance, idx = tree.query(point, k=number_of_neighbors)
        return distance, idx

    # Coordinates where to find neighbors
    if x_grid.ndim == 1 and y_grid.ndim == 1:
        x_grid, y_grid = np.meshgrid(x_grid, y_grid)

    stacked_xy = x_y_to_stacked_xy(x_grid, y_grid)
    grid_flat = grid_to_flat(stacked_xy)
    tree = cKDTree(grid_flat)

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list_nearest = executor.map(K_N_N_point, list_coord_station)
    except ModuleNotFoundError:
        list_nearest = map(K_N_N_point, list_coord_station)

    list_nearest = np.array([np.array(station) for station in list_nearest])
    list_index = [(x, y) for x in range(len(x_grid)) for y in range(len(y_grid))]

    index_nearest_neighbor = list_index[np.intp(list_nearest[0, 1])]

    return index_nearest_neighbor
