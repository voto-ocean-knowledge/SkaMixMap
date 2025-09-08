import datetime
import requests
import pandas as pd
import sys
import os
import numpy as np
from pathlib import Path
import logging
_log = logging.getLogger(__name__)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

rough_data = Path(root_dir) / "data" / "raw_location_data"
if not rough_data.exists():
    rough_data.mkdir(parents=True)
heincke_raw_csv = rough_data / "heincke_raw.csv"
processed_location_data = Path(root_dir) / "data" / "processed_location_data"
heincke_proc_csv = processed_location_data / "heincke.csv"

def heincke_download_data():
    begin_date = (datetime.datetime.now() - datetime.timedelta(hours=24)).isoformat()[:19]
    end_date = (datetime.datetime.now() + datetime.timedelta(hours=2)).isoformat()[:19]
    url = f"https://ingest.o2a-data.de/rest/data?codes=vessel:heincke:trimble_5228k50585:latitude&codes=vessel:heincke:trimble_5228k50585:longitude&datetimeMin={begin_date}&datetimeMax={end_date}&aggregate=MINUTE&aggregateFunctions=MEAN"
    print(url)
    req = requests.get(url)
    with open(heincke_raw_csv, "w", encoding="utf-8") as fout:
        fout.write(req.text)



def clean_locations(df):
    """
    Cleans out bad locations from a dataframe: nans, 0,0, Baltic GPS jamming artefacts
    :param df: pd.DataFrame with columns of lon and lat
    :return: cleaned df (drops rows)
    """
    before = len(df)
    df = df[(~np.isnan(df.lon)) & (~np.isnan(df.lat))] # nans
    df = df[~((df.lon>19.3) & (df.lat<55.4))] #GPS spoofing
    df = df[df.lat>1] # null island
    _log.info(f"Cleaning bad locations: removed {before - len(df)} rows of data ({round(100 * (1 - len(df)/before), 3)} %)")
    return df

def combine_heincke_data():
    df = pd.read_csv(heincke_raw_csv, parse_dates=['datetime'], encoding="utf-8", sep='\t')
    _log.info(f"reading in {len(df)} rows of downloaded data from R/V Heincke")
    df = df[['datetime',
             'vessel:heincke:trimble_5228k50585:longitude (mean) [°]',
             'vessel:heincke:trimble_5228k50585:latitude (mean) [°]', ]]
    df = df.rename({'vessel:heincke:trimble_5228k50585:longitude (mean) [°]': 'lon',
                    'vessel:heincke:trimble_5228k50585:latitude (mean) [°]': 'lat', }, axis=1)
    if heincke_proc_csv.exists():
        df_full = pd.read_csv(heincke_proc_csv, parse_dates=['datetime'], encoding="utf-8")
        df= df[df.datetime > df_full.datetime.max()]
    else:
        df_full = pd.DataFrame()
    if df.empty:
        _log.info("no new data from Heincke")
        return
    _log.info(f"adding {len(df)} rows of new locations from R/V Heincke")
    df_full = pd.concat([df_full, df])
    df_full = clean_locations(df_full)
    df_full.to_csv(heincke_proc_csv, index=False, encoding="utf-8")

def heincke_download_underway_data(start=datetime.datetime.now() - datetime.timedelta(hours=24), end=datetime.datetime.now() + datetime.timedelta(hours=2)):
    raw_csv = heincke_raw_csv
    start_new, end_new = heincke_download_check_times(start, end)
    begin_date = start_new.isoformat()[:19]
    end_date = end_new.isoformat()[:19]
    url = f"https://dashboard.awi.de/data-xxl/rest/data?beginDate={begin_date}&endDate={end_date}&aggregate=minute&aggregateFunctions=MEAN&sensors=vessel:heincke:trimble:longitude&sensors=vessel:heincke:trimble:latitude&sensors=vessel:heincke:tsg:sbe38:temperature&sensors=vessel:heincke:tsg:salinity"
    req = requests.get(url)
    with open(raw_csv, "w", encoding="utf-8") as fout:
        fout.write(req.text)  
    combine_heincke_data()   
    df = pd.read_csv(heincke_proc_csv, parse_dates=['datetime'], encoding="utf-8")
    df = df.rename({'vessel:heincke:trimble:longitude (mean) []': 'lon',
                    'vessel:heincke:trimble:latitude (mean) []': 'lat', 
                    'vessel:heincke:tsg:salinity (mean) [0/00]': 'salinity [PSU]',
                    'vessel:heincke:tsg:sbe38:temperature (mean) [°C]': 'temperature [°C]',
                    }, axis=1)
    df_sub = df[(df.datetime >= start) & (df.datetime <= end)]
    return df_sub

def heincke_download_check_times(start, end):
    try: 
        df = pd.read_csv(heincke_proc_csv, encoding='utf-8', parse_dates=['datetime'])
    except: return start, end
    start_new = df.datetime.min()
    end_new = end
    if start_new > end: 
        start_new = start
        end_new =  df.datetime.min()
    return start_new, end_new


def main():
    heincke_download_data()
    combine_heincke_data()

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