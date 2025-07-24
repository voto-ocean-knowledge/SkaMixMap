# SkaMixMap

### Current status

See the map at [https://voto-ocean-knowledge.github.io/SkaMixMap](https://voto-ocean-knowledge.github.io/SkaMixMap/) work in progress!

- Demo leaflet map with a couple of CMEMS satellite layers (hard coded dates! These are not the latest live datasets!)
- Demo location data pulled from a glider
- Demo location from old drifter unit read from email

### Steps to run locally

- Clone or download this repo
- Double click on index.html to see it in your browser
- ... that's it!
- If you want to remake/remix the input data, run the script [`src/make_demo_geojson.py`](https://github.com/voto-ocean-knowledge/SkaMixMap/blob/main/src/make_demo_geojson.py). Requirements are in requirements.txt

This repo hosts code for near real time visualisation of diverse surface and subsurface platform locations, as well as earth observation data, for field co-ordination during the SkaMix project.

Check out the [startup TODO list](https://github.com/voto-ocean-knowledge/SkaMixMap/issues/1) for action items


### Envisaged dataflow

1. nrt locations from drifters, autonomous platforms and vessels are emailed to votodatain@gmail.com in a variety of formats
2. Every hour, a python script running as a cronjob checks the inbox for new emails
3. The python script reads the email and converts the locations to geojson
4. geojson locations and tracks are displayed on a leaflet map
5. The leaflet map uses wmts web tiles to display multiple layers: bathy, SST, SSH etc.
6. Additional static plots are made with more detailed and scaled SST raster data from satellite/reanalysis products
7. SST from platforms is overlain on these plots where available


# Data sources

### Satellite data

Using WMTS system for nrt web tiled data. The first source is a CMEMS global reanalysis of temperature data. we are using two Baltic specific products from [SST TAC](https://marine.copernicus.eu/about/producers/sst-tac):

- L3 https://data.marine.copernicus.eu/product/SST_BAL_SST_L3S_NRT_OBSERVATIONS_010_032/description
- L4 https://data.marine.copernicus.eu/product/SST_BAL_SST_L4_NRT_OBSERVATIONS_010_007_b/services

We get SST from the [SL TAC](https://marine.copernicus.eu/about/producers/sl-tac)
- L4 Sea Surface Height and Dynamic Topography https://data.marine.copernicus.eu/product/SEALEVEL_EUR_PHY_L4_NRT_008_060/description


# Automation

### Getting data from emails

This requires a bit of setting up. Here's the prep work:

1. Create a gmail account that all incoming data will be sent to
2. Go to google account >> 2-step verification >> turn on 2-step verification
3. setup whatever 2FA you prefer
4. create an app password https://myaccount.google.com/u/7/apppasswords explained at https://support.google.com/accounts/answer/185833?hl=en
5. Copy that password into the secrets file `email_secrets.json` here in the root directory. It should look like

```json
{
  "email_username": "<account_name>@gmail.com",
  "email_password": "<16 char app password with no spaces>"
}
```

Now you're setup to read email from python with the `src/fetch_location_data.py` script
