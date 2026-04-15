def degrees_to_Kelvin(celsius):
    return celsius + 273.15

user_dicts = {

    'skamix':
    {
        "colorbar_limits": {
            "sst": {'min': degrees_to_Kelvin(15),
                    'max': degrees_to_Kelvin(18)},
            "sst_forecast": {'min': 15,
                             'max': 18},
            "sst_forecast_baltic": {'min': 15,
                                    'max': 18},
            "sss_forecast": {'min': 15,
                             'max': 35},
            "cdo_forecast": {'min': 0,
                             'max': 10},
        },
        "forecast_product_date": "2025-09-10",
        "satellite_product_date": "2025-09-10",
        "platforms_time_filter": {
            'start': "2025-09-01",
            'end': "2025-09-22"
        },

    },
    'skamix2':
        {
            "colorbar_limits" : {
                "sst": {'min': degrees_to_Kelvin(4),
                        'max': degrees_to_Kelvin(7)},
                "sst_forecast": {'min': 4,
                                 'max': 36.5},
                "sss_forecast": {'min': 20,
                                 'max': 35},
            },
            # "forecast_product_date": "2025-08-03",
            # "satellite_product_date": "2025-07-29"
            "platforms_time_filter": {
                'start': "2026-03-01",
                'end': "2026-06-01"
            },
        }
}
