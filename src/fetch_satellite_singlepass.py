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

# keep variable names/structure from the first script
rough_data = Path(root_dir) / "data" / "sat_singlepass"
if not rough_data.exists():
    rough_data.mkdir(parents=True)


mail_alarms_json = Path("mail_alarms.json")



def fetch_metop_sst_attachments():
    secrets_file = Path(root_dir) / "email_secrets.json"
    if not secrets_file.exists():
        _log.error(f"Did not find secrets file {secrets_file}. Cannot read emails. Skipping")
        return
    with open(f"{root_dir}/email_secrets.json", encoding="utf-8") as json_file:
        secrets = json.load(json_file)

    # connect to gmail and search for specific MetOp SST mails
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(secrets["email_username"], secrets["email_password"])
    except imaplib.IMAP4.error:
        _log.error(f"Incorrect credentials in {secrets_file}. Skipping email read")
        return

    mail.select("inbox")
    result, data = mail.search(None, '(OR SUBJECT "MetOp SST" SUBJECT "Fwd: MetOp SST")')
    mail_ids = data[0]
    id_list = mail_ids.split()
    if not id_list:
        _log.warning("No matching emails found. Skipping")
        return

    # check latest 10 emails
    for i in id_list[-15:]:
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
                # only the base name
                filename = os.path.basename(filename)
                ext = '.' + filename.split('.')[-1] if '.' in filename else None
                if ext not in ['.nc']: 
                        continue
                target_path = rough_data / filename
                if target_path.exists():
                    continue  # already saved
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                with open(target_path, 'wb') as fp:
                    fp.write(payload)
    return

if __name__ == '__main__':
    fetch_metop_sst_attachments()
