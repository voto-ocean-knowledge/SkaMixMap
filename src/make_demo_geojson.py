import datetime
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
json_dir = Path(folder)  / "static" / "skamix" / "json"
if not json_dir.exists():
    json_dir.mkdir(parents=True)

features_list = []

def write_geojson(features, filename, var_name = "platform_locations"):
    # Write out geojson to file with the syntax to make it importable in javascript. Ugly but functional
    file_out = json_dir / filename
    geojson_dict =  {
        "type": "FeatureCollection",
        "features": features
    }
    with open(file_out, "w") as fout:
        fout.write(f"var {var_name} =")
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
        self.outfile = "all_platform_locations.js"
        self.filter_json = False

    def process_json(self):
        for csv in loc_dir.glob("*.csv"):
            fn = csv.name
            df = pd.read_csv(csv, parse_dates=['datetime'])

            if self.filter_json:
                if 'platforms_time_filter' in user_dict.keys():
                    start = user_dict["platforms_time_filter"]['start']
                    end = user_dict["platforms_time_filter"]['end']
                else:
                    end = str(datetime.datetime.now())
                    start = str(datetime.datetime.now() - datetime.timedelta(days=3))
                df = time_filter(df, start, end)
                self.outfile = "platform_locations.js"
            if df.empty:
                continue

            line_style = {
                "weight": 4,
                "opacity": 0.8,
            }
            timestamp = str(df['datetime'].values[-1])[:19]
            if "heincke" in fn:
                line_popup =  f'<a href="https://www.awi.de/en/fleet-stations/research-vessel-and-cutter/research-vessel-heincke.html">R/V Heincke</a>'
                point_popup = f'<a href="https://www.awi.de/en/fleet-stations/research-vessel-and-cutter/research-vessel-heincke.html">R/V Heincke</a><br>location at <br>{timestamp}'
                line_style["color"] = "white"
            elif "skagerak" in fn:
                line_popup = f'<a href="https://www.gu.se/en/skagerak">R/V Skagerak</a>'
                point_popup = f'<a href="https://www.gu.se/en/skagerak">R/V Skagerak</a><br>location at <br>{timestamp}'
                line_style["color"] = "green"
            elif "SEA" in fn:
                glidermission = fn.split('.')[0]
                __, platform_id, mission_id = glidermission.split('_')
                line_popup = f"glider track <br> <a href='https://observations.voiceoftheocean.org/{platform_id}/{mission_id}'>{platform_id} {mission_id}</a>"
                point_popup = f"<a href='https://observations.voiceoftheocean.org/{platform_id}/{mission_id}'>{platform_id} {mission_id}</a><br>location at <br>{timestamp}"
                line_style["color"] = "#fffb08"
            elif "SB" in fn:
                glidermission = fn.split('.')[0]
                platform_id, mission_id, __ = glidermission.split('_')
                line_popup = f"glider track <br> <a href='https://observations.voiceoftheocean.org/{platform_id}/{mission_id}'>{platform_id} {mission_id}</a>"
                point_popup = f"<a href='https://observations.voiceoftheocean.org/{platform_id}/{mission_id}'>{platform_id} {mission_id}</a><br>location at <br>{timestamp}"
                line_style["color"] = "orange"
            elif "unit_" in fn:
                unit_id = fn.split('_')[1][:-4]
                line_popup = f"unit {unit_id}"
                point_popup =  f"unit {unit_id}<br>location at <br>{timestamp}"
            else:
                _log.warning(f"unkown data source {csv}. Skipping")
                continue

            line_dict = locations_to_geojson_line(df, line_popup, line_style)
            self.json_features_list.append(line_dict)
            point_dict = locations_to_geojson_point(df, point_popup)
            self.json_features_list.append(point_dict)

    def write_json(self):
        write_geojson(self.json_features_list, self.outfile, var_name = self.outfile.split('.')[0])



def create_info_string():
    info_string = "<h3>Age of platform location data</h3><ul>"
    for csv in loc_dir.glob("*.csv"):
        fn = csv.name.split('.')[0]
        now = datetime.datetime.now(datetime.timezone.utc)
        df = pd.read_csv(csv, parse_dates=['datetime'])
        # horrible hack to force localize datetime. Do not @ me
        df.index = df.datetime
        try:
            df = df.tz_localize('UTC')
        except TypeError:
            df = df
        last_update = df.index.max()
        time_diff = now - last_update
        days =  time_diff.days
        hours, rem = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        diff_str = ""
        if days:
            diff_str +=f"{days} days"
        if hours:
            diff_str += f" {hours} hours"
        if minutes:
            diff_str += f" {minutes} minutes"
        diff_str += f" {seconds} seconds"
        info = f"<li><b>{fn}</b> last location at {str(last_update)[:19]}, <b>{diff_str} ago</b><br></li>"
        info_string += info
    info_string += "</ul>"
    info_file = json_dir / "info.js"
    with open(info_file, "w") as fout:
        fout.write(f"var platform_times_info = '{info_string}';\n")


def main():
    create_info_string()
    json_maker = CreateGeojson()
    json_maker.process_json()
    json_maker.write_json()
    json_maker = CreateGeojson()
    json_maker.filter_json = True
    json_maker.process_json()
    json_maker.write_json()


if __name__ == '__main__':
    main()
