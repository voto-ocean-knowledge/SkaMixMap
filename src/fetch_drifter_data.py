import datetime
import pandas as pd
import imaplib
import json
import os
import sys
import email
from pathlib import Path
import mimetypes
import logging
_log = logging.getLogger(__name__)


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

rough_data = Path(root_dir) / "data" / "raw_mail_data"
if not rough_data.exists():
    rough_data.mkdir(parents=True)
processed_location_data = Path(root_dir) / "data" / "processed_location_data"
if not processed_location_data.exists():
    processed_location_data.mkdir(parents=True)

with open(f"{root_dir}/email_secrets.json") as json_file:
    secrets = json.load(json_file)

mail_alarms_json = Path("mail_alarms.json")

def extract_loc_from_body(fn):
    unit_id = None
    message_id = None
    lat = None
    lon = None
    dt = None
    with open(fn) as file_in:
        for line in file_in.readlines():
            if "Betreff" in line:
                unit_id = int(line.split(' ')[-1][:-1])
            if "MOMSN" in line:
                message_id = int(line.split(' ')[-1][:-1])
            if "Unit Location" in line:
                __, lat_str, lon_str = line.split(' = ')
                lat = float(lat_str.split(' ')[0])
                lon = float(lon_str[:-1])
            if "Time of Session" in line:
                time_str = line.split('(UTC): ')[-1][4:-1]
                dt =datetime.datetime.strptime(time_str, "%b %d %H:%M:%S %Y")
    if unit_id and message_id and lat and lon and dt:
        print(unit_id, message_id, dt, lat, lon)
    return

def extract_loc_from_sbd(fn):
    source = "sbd_file"
    name = fn.name
    filename = name.split('.')[0]
    unit_id, message_id = filename.split('_')
    unit_id = int(unit_id)
    message_id = int(message_id)
    with open(fn) as file_in:
        line = file_in.read()

    date_str, p, lat_lon_str = line.split(',')
    lat_lon_parts = lat_lon_str.split(' ')
    lat = float(lat_lon_parts[1])
    lon = float(lat_lon_parts[2])
    year = datetime.datetime.now().year
    # todo fix for demo data: setting this for 2024 for now (old messages)
    year = 2024
    dt = datetime.datetime(year, int(date_str[:2]), int(date_str[2:4]), int(date_str[4:6]), int(date_str[6:8]))

    ddict = {
        "unit_id": unit_id,
        "message_id": message_id,
        "source": source,
        "lat": lat,
        "lon":lon,
        "datetime": dt
    }

    unit_csv = processed_location_data / f"unit_{unit_id}.csv"
    if unit_csv.exists():
        df = pd.read_csv(unit_csv, parse_dates=["datetime"])
        existing_rows = df[(df['unit_id'] == unit_id) & (df['message_id'] == message_id) & (df['source'] == source) ]
        if existing_rows.empty:
            df.loc[len(df)] = ddict
    else:
        df = pd.DataFrame(ddict, index=[0])
    df = df.sort_values("message_id")
    df.to_csv(unit_csv, index=False)

def parse_mail():
    # Check gmail account for emails
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(secrets["email_username"], secrets["email_password"])
    mail.select("inbox")
    result, data = mail.search(None, '(SUBJECT "SBD Msg From Unit")')
    mail_ids = data[0]
    id_list = mail_ids.split()

    # check latest 10 emails
    for i in id_list[-10:]:
        msg = None
        result, data = mail.fetch(i, "(RFC822)")
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

        if not msg:
            continue
        counter = 1
        for part in msg.walk():
            # walk through the message looking for text and attachments
            # multipart/* are just containers
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if filename:
                ext = '.' + filename.split('.')[-1]
            else:
                ext = mimetypes.guess_extension(part.get_content_type())
                if not ext:
                    # Use a generic bag-of-bits extension
                    ext = '.bin'
                filename = f'part-{counter:03d}{ext}'
            counter += 1
            if ext not in ['.txt', '.sbd']:
                continue
            filename = rough_data / filename
            with open(filename, 'wb') as fp:
                fp.write(part.get_payload(decode=True))
            if  ext == '.txt':
                continue
                #extract_loc_from_body(filename)
            elif ext == '.sbd':
                extract_loc_from_sbd(filename)
    return


if __name__ == '__main__':
    parse_mail()