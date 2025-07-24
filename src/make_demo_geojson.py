import numpy as np
import pandas as pd
from pathlib import Path
import json
import os
import sys

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)
from fetch_heincke_data import heincke_proc_csv
data_dir = Path(folder) / 'data'
loc_dir = data_dir / "processed_location_data"

features_list = []

def write_geojson(features):
    # Write out geojson to file with the syntax to make it importable in javascript. Ugly but functional
    file_out = f"{folder}/data/demo/sample-geojson.js"
    geojson_dict =  {
        "type": "FeatureCollection",
        "features": features
    }
    with open(file_out, "w") as fout:
        fout.write("var input_locations =")
        json.dump(geojson_dict, fout)
        fout.write(';')
        
        
def lon_lat_to_coords(longitude, latitude):
    # convert lon and lat arrays to the coordinate pairs that geojson uses
    coords = []
    for lon, lat in zip(longitude, latitude):
        if np.isnan(lon) or np.isnan(lat):
            continue
        coords.append([lon, lat])
    return coords

def glider_locs_to_json():
    # Download sample glider data locations from VOTO ERDDAP
    df = pd.read_csv(
        "https://erddap.observations.voiceoftheocean.org/erddap/tabledap/nrt_SEA078_M29.csvp?latitude%2Clongitude%2Ctime")
    subsample = 100
    latitude = df['latitude (degrees_north)'].values[::subsample]
    longitude = df['longitude (degrees_east)'].values[::subsample]

    coords = lon_lat_to_coords(longitude, latitude)

    # make a geojson dict with locations, popup and styling

    line_dict = {
                "type": "Feature",
                "properties": {
                    "popupContent": f"glider track <br> <a href='https://observations.voiceoftheocean.org/SEA078/M29'>SEA078 M29</a>",
                    "style": {
                        "weight": 4,
                        "color": "#fffb08",
                        "opacity": 0.8,
                    },
                },
                "geometry": {"type": "LineString", "coordinates": coords},
    }
    point_dict = {
                "type": "Feature",
                "properties": {
                    "popupContent": f"<a href='https://observations.voiceoftheocean.org/SEA078/M29'>SEA078 M29</a><br>location at <br>{df['time (UTC)'].values[-1]}"
                },
                "geometry": {"type": "Point", "coordinates": [coords[-1][0], coords[-1][1]]
                }
            }
    features_list.append(line_dict)
    features_list.append(point_dict)


def drifter_locs_to_json():
    if not loc_dir.exists():
        return
    drifter_loc_files = list(loc_dir.glob("unit_*.csv"))
    if not drifter_loc_files:
        return
    for drifter_csv in drifter_loc_files:
        df = pd.read_csv(drifter_csv, parse_dates=['datetime'])
        unit_id = drifter_csv.name.split('_')[1][:-4]
        coords = lon_lat_to_coords(df.lon.values, df.lat.values)

        line_dict = {
            "type": "Feature",
            "properties": {
                "popupContent": f"unit {unit_id}",
                "style": {
                    "weight": 4,
                    "color": "#fd8050",
                    "opacity": 0.8,
                },
            },
            "geometry": {"type": "LineString", "coordinates": coords},
        }
        point_dict = {
            "type": "Feature",
            "properties": {
                "popupContent": f"unit {unit_id}<br>location at <br>{str(df['datetime'].values[-1])[:19]}"
            },
            "geometry": {"type": "Point", "coordinates": [coords[-1][0], coords[-1][1]]
                         }
        }
        features_list.append(line_dict)
        features_list.append(point_dict)
        
        
def heincke_locs_to_json():
    if not heincke_proc_csv.exists():
        return

    df = pd.read_csv(heincke_proc_csv, parse_dates=['datetime'])
    coords = lon_lat_to_coords(df.lon.values, df.lat.values)

    line_dict = {
        "type": "Feature",
        "properties": {
            "popupContent": f'<a href="https://www.awi.de/en/fleet-stations/research-vessel-and-cutter/research-vessel-heincke.html">R/V Heincke</a>',
            "style": {
                "weight": 4,
                "color": "white",
                "opacity": 0.8,
            },
        },
        "geometry": {"type": "LineString", "coordinates": coords},
    }
    point_dict = {
        "type": "Feature",
        "properties": {
            "popupContent": f'<a href="https://www.awi.de/en/fleet-stations/research-vessel-and-cutter/research-vessel-heincke.html">R/V Heincke</a><br>location at <br>{str(df["datetime"].values[-1])[:19]}'
        },
        "geometry": {"type": "Point", "coordinates": [coords[-1][0], coords[-1][1]]
                     }
    }
    features_list.append(line_dict)
    features_list.append(point_dict)


def main():
    glider_locs_to_json()
    drifter_locs_to_json()
    heincke_locs_to_json()
    write_geojson(features_list)


if __name__ == '__main__':
    main()
