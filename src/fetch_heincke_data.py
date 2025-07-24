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
    url = f"https://dashboard.awi.de/data-xxl/rest/data?beginDate={begin_date}&endDate={end_date}&aggregate=minute&aggregateFunctions=MEAN&sensors=vessel:heincke:trimble:longitude&sensors=vessel:heincke:trimble:latitude&sensors=vessel:heincke:saab:longitude&sensors=vessel:heincke:saab:latitude&sensors=vessel:heincke:phins:longitude&sensors=vessel:heincke:saab:latitude"
    req = requests.get(url)
    with open(heincke_raw_csv, "w") as fout:
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
    df = pd.read_csv(heincke_raw_csv, sep='\t', parse_dates=['datetime'])
    _log.info(f"reading in {len(df)} rows of downloaded data from R/V Heincke")
    df = df[['datetime',
             'vessel:heincke:trimble:longitude (mean) []',
             'vessel:heincke:trimble:latitude (mean) []', ]]
    df = df.rename({'vessel:heincke:trimble:longitude (mean) []': 'lon',
                    'vessel:heincke:trimble:latitude (mean) []': 'lat', }, axis=1)
    if heincke_proc_csv.exists():
        df_full = pd.read_csv(heincke_proc_csv, parse_dates=['datetime'])
        df= df[df.datetime > df_full.datetime.max()]
    else:
        df_full = pd.DataFrame()
    if df.empty:
        _log.info("no new data from Heicke")
        return
    _log.info(f"adding {len(df)} rows of new locations from R/V Heincke")
    df_full = pd.concat([df_full, df])
    df_full = clean_locations(df_full)
    df_full.to_csv(heincke_proc_csv, index=False)


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