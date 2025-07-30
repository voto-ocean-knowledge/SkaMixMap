import numpy as np
import pandas as pd
from pathlib import Path
import json
import os
import sys
import logging
_log = logging.getLogger(__name__)
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)
from user_variables import user_dict
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
        fout.write("var platform_locations =")
        json.dump(geojson_dict, fout)
        fout.write(';')


def time_filter(df, start, end):
    df = df[(df.datetime >= start) & (df.datetime <= end)]
    return df


def lon_lat_to_coords(longitude, latitude):
    # convert lon and lat arrays to the coordinate pairs that geojson uses
    coords = []
    for lon, lat in zip(longitude, latitude):
        if np.isnan(lon) or np.isnan(lat):
            continue
        coords.append([lon, lat])
    return coords


def locations_to_geojson_line(df, popup, style):

    coords = lon_lat_to_coords(df.lon.values, df.lat.values)

    line_dict = {
        "type": "Feature",
        "properties": {
            "popupContent": popup, 
            "style": style
        },
        "geometry": {"type": "LineString", "coordinates": coords},
    }
    return line_dict


def locations_to_geojson_point(df, popup):
    coords = lon_lat_to_coords(df.lon.values, df.lat.values)

    point_dict = {
        "type": "Feature",
        "properties": {
            "popupContent": popup
        },
        "geometry": {"type": "Point", "coordinates": [coords[-1][0], coords[-1][1]]
                     }
    }
    return point_dict


class CreateGeojson:
    def __init__(self):
        self.user_dict = user_dict
        self.json_features_list = []

    def process_json(self):
        for csv in loc_dir.glob("*.csv"):
            fn = csv.name
            df = pd.read_csv(csv, parse_dates=['datetime'])

            if 'platforms_time_filter' in user_dict.keys():
                start = user_dict["platforms_time_filter"]['start']
                end = user_dict["platforms_time_filter"]['end']
                df = time_filter(df, start, end)
            if df.empty:
                continue

            line_style = {
                "weight": 4,
                "opacity": 0.8,
            }
            if "heincke" in fn:
                line_popup =  f'<a href="https://www.awi.de/en/fleet-stations/research-vessel-and-cutter/research-vessel-heincke.html">R/V Heincke</a>'
                point_popup = f'<a href="https://www.awi.de/en/fleet-stations/research-vessel-and-cutter/research-vessel-heincke.html">R/V Heincke</a><br>location at <br>{str(df["datetime"].values[-1])[:19]}'
                line_style["color"] = "white"
            elif "glider" in fn:
                line_popup = f"glider track <br> <a href='https://observations.voiceoftheocean.org/SEA078/M29'>SEA078 M29</a>"
                point_popup = f"<a href='https://observations.voiceoftheocean.org/SEA078/M29'>SEA078 M29</a><br>location at <br>{df['datetime'].values[-1]}"
                line_style["color"] = "#fffb08"
            elif "unit_" in fn:
                unit_id = fn.split('_')[1][:-4]
                line_popup = f"unit {unit_id}"
                point_popup =  f"unit {unit_id}<br>location at <br>{str(df['datetime'].values[-1])[:19]}"
            else:
                _log.warning(f"unkown data source {csv}. Skipping")
                continue

            line_dict = locations_to_geojson_line(df, line_popup, line_style)
            self.json_features_list.append(line_dict)
            point_dict = locations_to_geojson_point(df, point_popup)
            self.json_features_list.append(point_dict)

    def write_json(self):
        write_geojson(self.json_features_list)
        

def main():
    json_maker = CreateGeojson()
    json_maker.process_json()
    json_maker.write_json()


if __name__ == '__main__':
    main()
