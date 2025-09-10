import requests
import pandas as pd
import numpy as np
import sys
import geopandas as gpd
import os
from pathlib import Path
import logging
_log = logging.getLogger(__name__)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

rough_data = Path(root_dir) / "data" / "raw_location_data"
if not rough_data.exists():
    rough_data.mkdir(parents=True)
skagerak_raw_csv = rough_data / "skagerak_raw.csv"
processed_location_data = Path(root_dir) / "data" / "processed_location_data"
skagerak_proc_csv = processed_location_data / "skagerak.csv"

def skagerak_download_data(records=100, return_df=True, remove_cached=True):
    url = f"https://postgrest-skagerak.apps.k8s.gu.se/sk_position?limit={records}&order=ts.desc"
    req = requests.get(url)
    json_data = req.json()
    gdf = gpd.GeoDataFrame(json_data)
    from shapely.geometry import shape
    gdf['geom'] = gdf['geom'].apply(shape)
    gdf = gpd.GeoDataFrame(gdf).set_geometry('geom')
    df = pd.DataFrame({'datetime': gdf.ts, 'lat': gdf.geometry.y, 'lon': gdf.geometry.x})
    df.index = (pd.to_datetime(df.datetime))
    df = df.tz_localize('UTC')
    df = df.drop('datetime', axis=1)
    df.to_csv(skagerak_raw_csv)
    if remove_cached:
        if skagerak_proc_csv.exists():
            skagerak_proc_csv.unlink()
    combine_skagerak_data()
    if return_df:
        df_full = pd.read_csv(skagerak_proc_csv, parse_dates=['datetime'], encoding="utf-8")
        return df_full


def combine_skagerak_data():
    df = pd.read_csv(skagerak_raw_csv, parse_dates=['datetime'], encoding="utf-8")
    _log.info(f"reading in {len(df)} rows of downloaded data from R/V Skagerak")
    if skagerak_proc_csv.exists():
        df_full = pd.read_csv(skagerak_proc_csv, parse_dates=['datetime'], encoding="utf-8")
        df= df[df.datetime > df_full.datetime.max()]
    else:
        df_full = pd.DataFrame()
    if df.empty:
        _log.info("no new data from Skagerak")
        return
    _log.info(f"adding {len(df)} rows of new locations from R/V Skagerak")
    df_full = pd.concat([df_full, df])
    df_full = df_full.sort_values("datetime")
    df_full.to_csv(skagerak_proc_csv, encoding="utf-8", index=False)

def skagerak_download_tsg_data(records=10000):
    url = f"https://postgrest-skagerak.apps.k8s.gu.se/sk_ferrybox?limit={records}&order=ts.desc"
    skagerak_download_data(records=records)
    req = requests.get(url)
    json_data = req.json()
    df = pd.DataFrame(json_data)
    df = df.rename({'ts': 'datetime'}, axis=1)
    df = df.sort_values("datetime")
    df.index = (pd.to_datetime(df.datetime))
    df = df.tz_localize('UTC')
    df = df.drop('datetime', axis=1)
    df_loc = pd.read_csv(skagerak_proc_csv, parse_dates=['datetime'])
    df_combi = pd.merge_asof(df, df_loc, left_on='datetime', right_on='datetime')
    df_combi = df_combi[~np.isnan(df_combi.lon)]
    return df_combi
    
    
    
def main():
    skagerak_download_data(remove_cached=False)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    main()