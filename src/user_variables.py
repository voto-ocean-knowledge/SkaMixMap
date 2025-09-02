def degrees_to_Kelvin(celsius):
    return celsius + 273.15

user_dict = {
    "colorbar_limits" : {
        "sst": {'min': degrees_to_Kelvin(13),
                'max': degrees_to_Kelvin(22)},
        "sst_forecast": {'min': 13,
                'max': 22},
        "sss_forecast": {'min': 15,
                         'max': 35},
    },
   # "forecast_product_date": "2025-08-03",
   # "satellite_product_date": "2025-07-29"
    #    "platforms_time_filter": {
#        'start': "2025-07-22",
#        'end': "2025-07-24"
#    },
}
