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


def extract_loc_from_body(fn):
    dfa = pd.read_html(fn)
    df = dfa[1]
    df_dict = {row[0]: row[1] for i, row in df.iterrows()}
    if 'Latitude' not in df_dict.keys():
        return
    ddict = {
        "lat": float(df_dict["Latitude"]),
        "lon": float(df_dict["Longitude"]),
        "datetime": pd.to_datetime(df_dict['Timestamp'])
    }

    unit_csv = processed_location_data / f"wirewalker.csv"
    if unit_csv.exists():
        df = pd.read_csv(unit_csv, parse_dates=["datetime"])
        if df.datetime.max() >= ddict['datetime']:
            return

        df.loc[len(df)] = ddict
        _log.info(f"adding wirewalker location  {ddict}")
    else:
        df = pd.DataFrame(ddict, index=[0])
    df = df.sort_values("datetime")
    df.to_csv(unit_csv, index=False)

    return


def wirewalker_locations_from_mail():
    secrets_file = Path(root_dir) / "email_secrets.json"
    if not secrets_file.exists():
        _log.error(f"Did not find secrets file {secrets_file}. Cannot read emails. Skipping")
        return
    with open(f"{root_dir}/email_secrets.json") as json_file:
        secrets = json.load(json_file)
    # Check gmail account for emails
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(secrets["email_username"], secrets["email_password"])
    except imaplib.IMAP4.error:
        _log.error(f"Incorrect credentials in {secrets_file}. Skipping email read")
        return
    mail.select("inbox")
    result, data = mail.search(None, '(SUBJECT "Xeos Forward - Goran WW")')
    mail_ids = data[0]
    id_list = mail_ids.split()
    if not id_list:
        _log.warning("No matching emails found. Skipping")
        return

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
            if ext not in ['.txt', '.html']:
                continue
            filename = rough_data / filename
            with open(filename, 'wb') as fp:
                fp.write(part.get_payload(decode=True))
            extract_loc_from_body(filename)
    return


def main():
    wirewalker_locations_from_mail()

if __name__ == '__main__':
    main()
