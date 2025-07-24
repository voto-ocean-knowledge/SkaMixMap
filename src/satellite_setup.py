import os
from pathlib import Path
import logging
import requests
import xmltodict
_log = logging.getLogger(__name__)

root_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

satellite_settings = root_dir / "satellite.js"
satellite_html = root_dir / "index.html"

def get_satellite_settings():
    satellite_dicts = {'sst_l4': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SST_BAL_SST_L4_NRT_OBSERVATIONS_010_007_b/DMI-BALTIC-SST-L4-NRT-OBS_FULL_TIME_SERIE',
        'var_name': 'analysed_sst'},
        'sst_l3': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SST_BAL_SST_L3S_NRT_OBSERVATIONS_010_032/DMI-BALTIC-SST-L3S-NRT-OBS_FULL_TIME_SERIE_201904',
        'var_name': 'sea_surface_temperature'},
        'ssh_l4': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SEALEVEL_EUR_PHY_L4_NRT_008_060/cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.0625deg_P1D_202506',
        'var_name': 'sla'},
        'adt_l4': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SEALEVEL_EUR_PHY_L4_NRT_008_060/cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.0625deg_P1D_202506',
        'var_name': 'adt'}}
   # if 'analysed_sst' in ddict['ows:Identifier'] or 'sea_surface_temperature' in ddict['ows:Identifier']:
    for layer_name, sat_dict in satellite_dicts.items():
        req = requests.get(f"{sat_dict['url']}?request=GetCapabilities&service=WMS")
        wms = xmltodict.parse(req.text)
        for cap_dict in wms['Capabilities']['Contents']['Layer']:
            if sat_dict['var_name'] == cap_dict['ows:Identifier'].split('/')[-1]:
                layer_dict = cap_dict
        sat_dict['title'] = layer_dict['ows:Title']
        sat_dict["layer_datetime"] = layer_dict['Dimension']['Default']
        sat_dict["min_val"] = float(layer_dict['ows:Metadata']['VariableInformation']['MinimumValue'])
        sat_dict["max_val"] = float(layer_dict['ows:Metadata']['VariableInformation']['MaximumValue'])
        _log.info(f"satellite layer info {layer_name}: {sat_dict}")
    return satellite_dicts

def write_satellite_settings(ddict):
    
    with open(satellite_settings, "w") as fout:
        for key, var in ddict.items():
            fout.write(f"var {key}_time = '{var['layer_datetime']}';\n")

def write_sat_to_html(ddict):
    with open(satellite_html, "r") as f:
        contents = f.readlines()
    new_info = "<h3>satellite product times 🛰️</h3><ul>"
    for key, var in ddict.items():
        dt = var['layer_datetime'][:11]
        newstr = f"<li><b>{key}</b> date: <b>{dt}</b> min: <b>{round(var['min_val'], 3)}</b> max: <b>{round(var['max_val'], 3)}</b> variable: {var['title']} </li>"
        new_info += newstr
    new_info+='</ul>\n'
    for i, item in enumerate(contents):
        if "satellite product times" in item:
            contents[i] = new_info

    with open(satellite_html, "w") as f:
        contents = "".join(contents)
        f.write(contents)


def main():
    sat_dicts = get_satellite_settings()
    write_satellite_settings(sat_dicts)
    write_sat_to_html(sat_dicts)


if __name__ == '__main__':
    main()
