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
import fetch_heincke_data

def main():
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
    fetch_heincke_data.main()
    fetch_voto_data.main()
    make_demo_geojson.main()
    satellite_setup.main()
    end = datetime.datetime.now()
    _log.info(f"END elapsed time: {round((end - start).total_seconds(), 1)} seconds")

if __name__ == '__main__':
    main()