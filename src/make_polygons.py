from pathlib import Path
import xarray as xr
import pandas as pd
import datetime
import requests
import numpy as np
import os
import matplotlib.pyplot as plt
import json
from shapely.geometry import Polygon
import geopandas as gpd
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

path_to_emodnet = Path("/data/temp/D5_2024.nc")



def bathy_to_geojson(extent=[57.4, 59, 8, 12], depths=(100, 200), directory=Path("")):
    gebco = xr.open_dataset(path_to_emodnet)
    print("Subsettting emodnet data")
    ds = gebco.sel(lon=slice(extent[2], extent[3]), lat=slice(extent[0], extent[1]))
    lon = ds.lon
    lat = ds.lat
    topo =  - ds.elevation
    for depth in depths:
        print(str(directory) + "depth " + str(depth))
        # create single contour level plot. Hack to force closers of polygons
        edit = topo.copy()
        edit[0, :] = depth - 1
        edit[-1, :] = depth - 1
        edit[:, 0] = depth - 1
        edit[:, -1] = depth - 1
        fig, ax = plt.subplots()
        cs = ax.contour(lon, lat, edit, [depth])
        shapes = cs.allsegs[0]
        lines = []
        print("extracting geometries")
        for v in shapes:
            if len(v) < 4:
                # Trying to write less than 4 points to a polygon fails, skip these
                continue
            lines.append(Polygon(v))

        # create geopandas dataframe and write it to json
        line_gdf = gpd.GeoDataFrame(geometry=lines)
        geo_json = line_gdf.to_json()
        print("writing to file")
        # create mission directory if it doesn't exist already
        isobaths_dir = Path(directory) / 'isobaths'
        if not isobaths_dir.exists():
            isobaths_dir.mkdir(parents=True)
        with open(isobaths_dir/ (str(abs(depth)) + 'm.json'), 'w', encoding='utf-8') as f:
            json.dump(geo_json, f)


def fetch_ftle():
    response = requests.get('https://hyrax.iow.de/opendap/hyrax/dataset_00075/dataset_00075_data/file_0001.nc')
    with open("/data/temp/ftle.nc", mode="wb") as file:
        file.write(response.content)

    
def ftle_grad_to_polygons(directory):
    if not directory.exists():
        directory.mkdir(parents=True)
    ftle_vars_dict = {
        'temp_grad': {'var_name': 'temp_grad',
                     'thresholds': [1e-4, 2e-4, 3e-4],
                      'color_dict': ['#FFA0A0', '#FF5050', '#FF0000'],
                      },
        'salt_grad': {'var_name': 'salt_grad',
                      'thresholds': [1e-4, 2e-4, 3e-4],
                      'color_dict': ['#A0A0FF', '#5050FF', '#0000FF'],
                      },
        'ftle': {'var_name': 'ftle',
                 'thresholds': [2e-5, 4e-5, 6e-5],
                 'color_dict': ['#FFFFFF', '#808080', '#000000'],
                 },
    }
    ds = xr.open_dataset("/data/temp/ftle.nc")
    timesteps = pd.date_range("2026-01-01T14:00:00", "2027-01-03T14:00:00")
    timesteps = timesteps[timesteps > np.datetime64(datetime.datetime.now())][:3]
    for day, timestep in enumerate(timesteps):
        lines = []
        for var_name, var_dict in ftle_vars_dict.items():
            for i, threshold in enumerate(var_dict['thresholds']):
                variable = ds[var_name].loc[timestep]
                var_copy = variable.copy()
                var_copy = var_copy.fillna(0)
                fig, ax = plt.subplots()
                cs = ax.contour(ds.lon, ds.lat, var_copy, [threshold])
                shapes = cs.allsegs[0]
                for v in shapes:
                    if len(v) < 4:
                        # Trying to write less than 4 points to a polygon fails, skip these
                        continue
                    popup = f"{var_name} > {threshold}<br>{str(timestep)[:10]}"
                    coords = [[point[0], point[1]] for point in v]

                    polygon = {
                        "geometry": {"type": "Polygon", "coordinates": [coords]},
                        "type": "Feature",
                        "properties": {
                            "popupContent": popup,
                            "color": var_dict['color_dict'][i],
                        },
                    }
                    lines.append(polygon)
                plt.close('all')
        poly_dict = {"type": "FeatureCollection", "features": lines}

        with open(directory /  f'ftle_{day}.json', 'w', encoding='utf-8') as f:
            json.dump(poly_dict, f)


if __name__ == '__main__':
    out_dir = data_dir = Path(folder) / 'static' / 'skamix2' / 'json'
    #fetch_ftle()
    ftle_grad_to_polygons(out_dir / 'ftle')
    #bathy_to_geojson(directory=out_dir)