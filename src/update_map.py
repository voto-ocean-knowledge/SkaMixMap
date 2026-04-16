import os
import sys
import logging
import datetime
_log = logging.getLogger(__name__)
folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, folder)
import make_demo_geojson
import fetch_drifter_data
import fetch_voto_data
import satellite_setup
import fetch_wirewalker_data
import fetch_emb_data
import fetch_garmin_drifter_data

def main():
    skamix_dir = "skamix2"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    start = datetime.datetime.now()
    _log.info("START")
    fetch_drifter_data.main()
    _log.info(f"fetched drifters. Elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")
    fetch_emb_data.main()
    _log.info(f"fetched emb. Elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")
    fetch_garmin_drifter_data.main()
    _log.info(f"fetched garmin drifters. Elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")
    fetch_wirewalker_data.main()
    _log.info(f"fetched wirewalker. Elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")
    make_demo_geojson.main(skamix_dir=skamix_dir)
    _log.info(f"made demo geojson. Elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")
    satellite_setup.main(skamix_dir=skamix_dir)
    _log.info(f"fetched satellite. Elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")

    _log.info(f"END elapsed time: {round(( datetime.datetime.now() - start).total_seconds(), 1)} seconds")

if __name__ == '__main__':
    main()