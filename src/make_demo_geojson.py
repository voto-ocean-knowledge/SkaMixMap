import numpy as np
import pandas as pd
import json
import os
import sys

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)

def glider_locs_to_json():
    # Download sample glider data locations from VOTO ERDDAP
    df = pd.read_csv(
        "https://erddap.observations.voiceoftheocean.org/erddap/tabledap/nrt_SEA078_M29.csvp?latitude%2Clongitude%2Ctime")
    subsample = 100
    latitude = df['latitude (degrees_north)'].values[::subsample]
    longitude = df['longitude (degrees_east)'].values[::subsample]

    coords = []
    for lon, lat in zip(longitude, latitude):
        if np.isnan(lon) or np.isnan(lat):
            continue
        coords.append([lon, lat])

    # make a geojson dict with locations, popup and styling

    line_dict = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {"type": "LineString", "coordinates": coords},
                "type": "Feature",
                "properties": {
                    "popupContent": f"glider track <br> <a href='https://observations.voiceoftheocean.org/SEA078/M29'>SEA078 M29</a>",
                    "style": {
                        "weight": 4,
                        "color": "#fffb08",
                        "opacity": 0.8,

                    },
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "popupContent": f"SEA078 location at <br>{df['time (UTC)'].values[-1]}"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }
        ],
    }

    # Write out geojson to file with the syntax to make it importable in javascript. Ugly but functional
    file_out = f"{folder}/data/demo/sample-geojson.js"
    with open(file_out, "w") as fout:
        fout.write("var input_locations =")
        json.dump(line_dict, fout)
        fout.write(';')
        
if __name__ == '__main__':
    glider_locs_to_json()