import pandas as pd
import os
from pathlib import Path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


processed_location_data = Path(root_dir) / "data" / "processed_location_data"
def download_glider_data(dataset_id = "nrt_SEA078_M29"):
    # Download sample glider data locations from VOTO ERDDAP
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?latitude%2Clongitude%2Ctime")
    df = df[::100]
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    glider_csv = processed_location_data / (dataset_id + ".csv")
    df.to_csv(glider_csv, index=False)
    
    
def glider_download_nrt_data(dataset_id="nrt_SEA078_M29"):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?latitude%2Clongitude%2Ctime%2Cdepth%2Ctemperature%2Csalinity")
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    df['datetime'] = pd.to_datetime(df.datetime)
    return df


    


def download_sailbuoy_data(dataset_id = "SB2120_M3_delayed"):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?time%2Clatitude%2Clongitude&time%3E=2024-07-16&time%3C=2024-07-17")
    df = df[::100]
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    sailbuoy_csv = processed_location_data / (dataset_id + ".csv")
    df.to_csv(sailbuoy_csv, index=False)

    
def sailbuoy_download_nrt_data(dataset_id="SB2120_M3_delayed"):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?time%2Clatitude%2Clongitude%2CTEMP&time%3E=2024-07-16&time%3C=2024-07-17")
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    df['datetime'] = pd.to_datetime(df.datetime)
    return df

def main():
    download_sailbuoy_data()
    download_glider_data()
    download_glider_data(dataset_id= "nrt_SEA069_M52") # for the already deployed Skagerak glider

if __name__ == '__main__':
    main()