import pandas as pd
import os
from pathlib import Path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


processed_location_data = Path(root_dir) / "data" / "processed_location_data"
def download_glider_data(dataset_id = "nrt_SEA078_M29", surface_upcast_data_only=False):
    # Download glider data locations from VOTO ERDDAP
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?latitude%2Clongitude%2Ctime%2Cprofile_num%2Ctemperature%2Cdepth%2Cnav_state",
        parse_dates=['time (UTC)'])
    if surface_upcast_data_only:
        # Filter to only data when glider going up in uppermost 10 m. Necessary for good SST estimate
        df = df[df['depth (m)'] < 10]
        df = df[df['nav_state (None)'] == 117]
    df = df.groupby('profile_num (1)').median()
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'temperature (Celsius)': 'TEMP',
                    'time (UTC)': 'datetime'}, axis=1)
    df['datetime'] = pd.to_datetime(df.datetime).dt.round('1s')
    glider_csv = processed_location_data / (dataset_id + ".csv")
    df.to_csv(glider_csv, index=False)
    
    
def glider_download_nrt_data(dataset_id="nrt_SEA044_M109"):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?latitude%2Clongitude%2Ctime%2Cdepth%2Ctemperature%2Csalinity")
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'time (UTC)': 'datetime'}, axis=1)
    return df


def download_sailbuoy_data(dataset_id = "SB2121_20250905T0539_R", return_df=True):
    df = pd.read_csv(
        f"https://erddap.observations.voiceoftheocean.org/erddap/tabledap/{dataset_id}.csvp?time%2Clatitude%2Clongitude%2CTEMP")
    df = df.rename({'longitude (degrees_east)': 'lon',
                    'latitude (degrees_north)': 'lat',
                    'TEMP (degree_C)': 'TEMP',
                    'time (UTC)': 'datetime'}, axis=1)
    sailbuoy_csv = processed_location_data / (dataset_id + ".csv")
    df.to_csv(sailbuoy_csv, index=False)
    if return_df:
        return df


def main():
    download_sailbuoy_data(return_df=False)
    download_glider_data(dataset_id= "nrt_SEA044_M109", surface_upcast_data_only=True)
    download_glider_data(dataset_id= "nrt_SEA069_M52", surface_upcast_data_only=True) # for the already deployed Skagerak glider
    download_glider_data(dataset_id= "nrt_SEA068_M46", surface_upcast_data_only=True) #  Deployed 2025-09-10

if __name__ == '__main__':
    main()