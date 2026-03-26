import json
import requests
import xmltodict
import pandas as pd
from pathlib import Path
import logging
import os
_log = logging.getLogger(__name__)
root_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

rough_data = root_dir / "data" / "raw_location_data"
if not rough_data.exists():
    rough_data.mkdir(parents=True)
heincke_raw_csv = rough_data / "heincke_raw.csv"
processed_location_data = root_dir / "data" / "processed_location_data"
heincke_proc_csv = processed_location_data / "heincke.csv"

floats = {'Eddy_2062': 'Eddy 2062 - GA 021',
          'Bernd':'GA 011-Bernd'}

def fetch_garmin_drifters():
    auth_file = root_dir / 'email_secrets.json'
    if not auth_file.exists():
        _log.error(f"No auth found in {auth_file} aborting")
        return
    with open(auth_file) as f:
        auth = json.load(f)
    response = requests.get('https://share.garmin.com/Feed/Share/RUM49', auth=(auth['garmin_user'], auth['garmin_password']))
    dict_data = xmltodict.parse(response.content)
    kml = dict_data['kml']
    float_id, lon, lat, dt = [], [], [], []
    for drifter_dict in kml['Document']['Folder']:
        for placemark in drifter_dict['Placemark']:
            if 'TimeStamp' in placemark.keys():
                float_id.append(placemark['name'])
                dt.append(placemark['TimeStamp']['when'])
                extra_data = placemark['ExtendedData']['Data']
                for ddict in extra_data:
                    if ddict['@name'] == 'Latitude':
                        lat.append(ddict['value'])
                    elif ddict['@name'] == 'Longitude':
                        lon.append(ddict['value'])

    df = pd.DataFrame({'float_id': float_id, 'datetime': dt, 'lon': lon, 'lat': lat})
    df['datetime'] = pd.to_datetime(df.datetime)
    df = df.sort_values('datetime')
    for float_name, float_id in floats.items():
        df_float = df[df.float_id == float_id][['datetime', 'lon', 'lat']]
        if df_float.empty:
            continue
        outfile = rough_data / f"drifter_{float_name}.csv"
        df_float.to_csv(outfile, index=False)


def combine_drifter_data():
    for drifter_file in rough_data.glob("*drifter*"):
        fn = drifter_file.name
        drifter_name = fn.split('.')[0].replace('drifter_', '')
        df = pd.read_csv(drifter_file, parse_dates=['datetime'])
        _log.info(f"reading in {len(df)} rows of downloaded data from drifter {drifter_name}")
        proc_file = processed_location_data / fn
        if proc_file.exists():
            df_full = pd.read_csv(proc_file)
            df= df[df.datetime > df_full.datetime.max()]
        else:
            df_full = pd.DataFrame()
        if df.empty:
            _log.info(f"no new data from drifter{drifter_name}")
            return
        _log.info(f"adding {len(df)} rows of new locations from drifter {drifter_name}")
        df_full = pd.concat([df_full, df])
        df_full.to_csv(proc_file, index=False)


def main():
    fetch_garmin_drifters()
    combine_drifter_data()

if __name__ == '__main__':
    main()
