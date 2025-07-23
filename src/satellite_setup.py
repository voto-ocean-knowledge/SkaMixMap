import os
from pathlib import Path
import logging
_log = logging.getLogger(__name__)

root_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

satellite_settings = root_dir / "satellite.js"
satellite_html = root_dir / "index.html"

def get_satellite_settings():
    ddict = {
        'l4_sst': '2025-07-20T12:00:00.000Z',
        'l3_sst': '2025-07-22T00:00:00.000Z',
    }
    return ddict

def write_satellite_settings(ddict):
    
    with open(satellite_settings, "w") as fout:
        for key, var in ddict.items():
            fout.write(f"var {key} = '{var}';\n")

def write_sat_to_html(ddict):
    with open(satellite_html, "r") as f:
        contents = f.readlines()
    new_info = "<br><b>satellite product times</b>:<br>"
    for key, var in ddict.items():
        newstr = f"{key} satellite product from {var}<br>"
        new_info += newstr
    new_info+='\n'
    for i, item in enumerate(contents):
        if "satellite product times" in item:
            contents[i] = new_info

    with open(satellite_html, "w") as f:
        contents = "".join(contents)
        f.write(contents)
        
if __name__ == '__main__':
    sat_dict = get_satellite_settings()
    write_satellite_settings(sat_dict)
    write_sat_to_html(sat_dict)