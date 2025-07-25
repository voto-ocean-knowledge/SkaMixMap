import pandas as pd
import os
from pathlib import Path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


processed_location_data = Path(root_dir) / "data" / "processed_location_data"
glider_csv = processed_location_data / "glider.csv"
def download_glider_data():
    # Download sample glider data locations from VOTO ERDDAP
    df = pd.read_csv(
        "https://erddap.observations.voiceoftheocean.org/erddap/tabledap/nrt_SEA078_M29.csvp?latitude%2Clongitude%2Ctime")
    df = df[::100]
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    df.to_csv(glider_csv, index=False)

def main():
    download_glider_data()

if __name__ == '__main__':
    main()