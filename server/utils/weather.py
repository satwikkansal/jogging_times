import os

import pyowm

owm = None


def get_owm_client():
    global owm
    if owm is None:
        api_key = os.getenv('OWM_API_KEY')
        assert api_key is not None
        owm = pyowm.OWM(api_key)
    return owm


def get_current_weather_at_location(lat, lng):
    client = get_owm_client()
    weather_result = client.weather_at_coords(lat, lng).get_weather()
    return weather_result.to_JSON()
