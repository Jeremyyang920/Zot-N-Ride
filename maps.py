import json
import urllib.parse
import urllib.request
from os import environ

UCI_PLACE_ID = 'ChIJkb-SJQ7e3IAR7LfattDF-3k'
BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
GOOGLE_API_KEY = environ.get('GOOGLE_API_KEY')
def calc_driving_time(source: str, destination: str) -> int:
    query_parameters = [('origins',source), ('destinations',destination), ('key',GOOGLE_API_KEY)]
    url = BASE_URL + urllib.parse.urlencode(query_parameters)
    json_to_read = get_json(url)
    return json_to_read['rows'][0]['elements'][0]['duration']['value']

def get_json(url: str) -> dict:
    response = None
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode(encoding='utf-8'))
    finally:
        if response != None:
            response.close()
