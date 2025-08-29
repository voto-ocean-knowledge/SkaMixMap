import pandas as pd
import os
from pathlib import Path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


processed_location_data = Path(root_dir) / "data" / "processed_location_data"
glider_csv = processed_location_data / "glider.csv"
def download_glider_data(dataset_id = "nrt_SEA078_M29"):
    # Download sample glider data locations from VOTO ERDDAP
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?latitude%2Clongitude%2Ctime")
    df = df[::100]
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    df.to_csv(glider_csv, index=False)
    
def glider_download_nrt_data(dataset_id="nrt_SEA078_M29"):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?latitude%2Clongitude%2Ctime%2Cdepth%2Ctemperature%2Csalinity")
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    df['datetime'] = pd.to_datetime(df.datetime)
    return df

def main():
    download_glider_data()

if __name__ == '__main__':
    main()