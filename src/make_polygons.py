from pathlib import Path
import xarray as xr
import os
import matplotlib.pyplot as plt
import json
from shapely.geometry import Polygon
import geopandas as gpd
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

path_to_emodnet = Path("/home/callum/Documents/datasets/bathy/emodet_2024/D5_2024.nc")



def bathy_to_geojson(extent=[57, 59, 8, 12], depths=(180, 200, 220), directory=Path("")):
    gebco = xr.open_dataset(path_to_emodnet)
    print("Subsettting emodnet data")
    ds = gebco.sel(lon=slice(extent[2], extent[3]), lat=slice(extent[0], extent[1]))
    lon = ds.lon
    lat = ds.lat
    topo =  - ds.elevation
    for depth in depths:
        print(str(directory) + "depth " + str(depth))
        # create single contour level plot
        fig, ax = plt.subplots()
        cs = ax.contour(lon, lat, topo, [depth])
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

def ftle_grad_to_polygons(directory):
    ds = xr.open_dataset("/home/callum/Downloads/ftle_data.nc")
    threshold = 0.0002
    ds.temp_grad[-1, :, :].plot()
    fig, ax = plt.subplots()
    cs = ax.contour(ds.lon, ds.lat, ds.temp_grad[-1,:,:], [threshold])
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
    if not directory.exists():
        directory.mkdir(parents=True)
    with open(directory/  'ftle_temp.json', 'w', encoding='utf-8') as f:
        json.dump(geo_json, f)


if __name__ == '__main__':
    out_dir = data_dir = Path(folder) / 'static' / 'skamix2' / 'json'
    ftle_grad_to_polygons(out_dir / 'ftle')
    bathy_to_geojson(directory=out_dir)