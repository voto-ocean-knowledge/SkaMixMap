import os
from pathlib import Path
import logging
import requests
import xmltodict
import matplotlib.pyplot as plt
import numpy as np
import cmocean.cm as cmo
_log = logging.getLogger(__name__)

root_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from user_variables import user_dict

manual_limits = user_dict['colorbar_limits']

satellite_settings = root_dir / "static" / "satellite.js"
satellite_html = root_dir / "index.html"

def get_satellite_settings():
    satellite_dicts = {'sst_l4': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SST_BAL_SST_L4_NRT_OBSERVATIONS_010_007_b/DMI-BALTIC-SST-L4-NRT-OBS_FULL_TIME_SERIE',
        'var_name': 'analysed_sst'},
        'sst_l3': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SST_ATL_PHY_L3S_NRT_010_037/cmems_obs-sst_atl_phy_nrt_l3s_P1D-m_202211',
        'var_name': 'sea_surface_temperature'},
        'ssh_l4': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SEALEVEL_EUR_PHY_L4_NRT_008_060/cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.0625deg_P1D_202506',
        'var_name': 'sla'},
        'adt_l4': {
        'url': 'https://wmts.marine.copernicus.eu/teroWmts/SEALEVEL_EUR_PHY_L4_NRT_008_060/cmems_obs-sl_eur_phy-ssh_nrt_allsat-l4-duacs-0.0625deg_P1D_202506',
        'var_name': 'adt'},
        'chl_l4': {
            'url': 'https://wmts.marine.copernicus.eu/teroWmts/OCEANCOLOUR_ATL_BGC_L4_NRT_009_116/cmems_obs-oc_atl_bgc-plankton_nrt_l4-gapfree-multi-1km_P1D_202311',
            'var_name': 'CHL'},
    }
   # if 'analysed_sst' in ddict['ows:Identifier'] or 'sea_surface_temperature' in ddict['ows:Identifier']:
    for layer_name, sat_dict in satellite_dicts.items():
        req = requests.get(f"{sat_dict['url']}?request=GetCapabilities&service=WMS")
        wms = xmltodict.parse(req.text)
        for cap_dict in wms['Capabilities']['Contents']['Layer']:
            if sat_dict['var_name'] == cap_dict['ows:Identifier'].split('/')[-1]:
                layer_dict = cap_dict
        sat_dict['title'] = layer_dict['ows:Title']
        if "satellite_product_date" in user_dict.keys():
             sat_dict["layer_datetime"] = user_dict["satellite_product_date"] + "T00:00:00.000Z"
        else:
            sat_dict["layer_datetime"] = layer_dict['Dimension']['Default']
        sat_dict["min_val"] = float(layer_dict['ows:Metadata']['VariableInformation']['MinimumValue'])
        sat_dict["max_val"] = float(layer_dict['ows:Metadata']['VariableInformation']['MaximumValue'])
        sat_dict["units"] = layer_dict['ows:Metadata']['VariableInformation']['Unit']
        if layer_dict['Style']:
            if type(layer_dict['Style']) is dict:
                sat_dict['cmap'] =  layer_dict['Style']['ows:Identifier'].split(':')[-1]
            elif layer_dict['Style'][0]['@isDefault'] == 'true':
                sat_dict['cmap'] =  layer_dict['Style'][0]['ows:Identifier'].split(':')[-1]
        _log.info(f"satellite layer info {layer_name}: {sat_dict}")
    return satellite_dicts

def write_satellite_settings(ddict):
    with open(satellite_settings, "w") as fout:
        for key, var in ddict.items():
            fout.write(f"var {key}_time = '{var['layer_datetime']}';\n")
        for var_name, limits_dict in manual_limits.items():
            for key, var in limits_dict.items():
                fout.write(f"{var_name}_{key} = {var};\n")



def write_graticule_settings():
    with open(satellite_settings, "a") as fout:
        levels = range(4, 15)
        initial_lat_spacing = 8
        lon_spacing_multiplier = 2
        lat_list = []
        lon_list = []
        spacing = initial_lat_spacing
        for level in levels:
            lat_list.append({'start': level, 'end': level, 'interval': spacing})
            lon_list.append({'start': level, 'end': level, 'interval': spacing * lon_spacing_multiplier})
            spacing = spacing/2
        graticule_dict = {'latitude': lat_list,
                          'longitude': lon_list}
        fout.write(f"var graticule_dict = {graticule_dict};\n")


def write_sat_to_html(ddict):
    with open(satellite_html, "r") as f:
        contents = f.readlines()
    new_info = "<h3>satellite product times and data ranges 🛰️</h3><ul>"
    for key, var in ddict.items():
        dt = var['layer_datetime'][:16]
        newstr = f"<li><b>{key}</b> date: <b>{dt}</b> min: <b>{round(var['min_val'], 3)}</b> max: <b>{round(var['max_val'], 3)}</b> variable: {var['title']} </li>"
        new_info += newstr
    new_info+='</ul>\n'
    for i, item in enumerate(contents):
        if "satellite product times" in item:
            contents[i] = new_info

    with open(satellite_html, "w") as f:
        contents = "".join(contents)
        f.write(contents)

def make_color_bars(ddict):
    fig, ax = plt.subplots()
    step = 0
    standard_cmaps = plt.colormaps()
    for key, layer_dict in ddict.items():
        if key == 'sst_l3':
            continue
        label = f"{key} {layer_dict['title']} [{layer_dict['units']}]"
        step += 1
        cmap = layer_dict['cmap']
        if cmap not in standard_cmaps:
            cmap = f"cmo.{cmap}"
        vmin = layer_dict['min_val']
        vmax = layer_dict['max_val']
        if key[:3] in manual_limits.keys():
            vmin = manual_limits[key[:3]]['min']
            vmax = manual_limits[key[:3]]['max']
        x = np.linspace(vmin, vmax, 100)[np.newaxis, :]
        mappable = ax.imshow(x, aspect='auto', cmap=cmap)
        cbar_ax = fig.add_axes([0.15, 0.25 - 0.18 * step, 1, 0.08])
        plt.colorbar(cax=cbar_ax, mappable=mappable, orientation='horizontal', label=label)
    ax.remove()
    plt.savefig(root_dir / "static" / "colorbars.png", bbox_inches="tight", transparent=True)


def main():
    sat_dicts = get_satellite_settings()
    write_satellite_settings(sat_dicts)
    write_sat_to_html(sat_dicts)
    make_color_bars(sat_dicts)
    make_color_bars(sat_dicts)
    write_graticule_settings()


if __name__ == '__main__':
    main()
