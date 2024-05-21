import requests
import json
import re

from settings import KEY_YANDEX_MAP

def get_city(address):
    key_yandex_map = KEY_YANDEX_MAP
    geocoder_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": key_yandex_map,
        "format": "json",
        "geocode": address
    }
    response = requests.get(geocoder_url, params=params)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data["response"]["GeoObjectCollection"]["featureMember"]:
            geoObject = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            try:
                city = geoObject["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["Locality"]["LocalityName"]
                re_city = re_find_name(city)
                return re_city
            except: 
                region = geoObject["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["AdministrativeAreaName"]
                return region
        else:
            msg_error = 'Не удалось определить город из адреса'
            return msg_error
    else:
        msg_error = f"Ошибка запроса: {response.status_code}"
        return msg_error
    
def re_find_name(name):
    pattern = r'\b[А-ЯЁ]\w*\b'
    match = re.search(pattern, name)
    if match:
        word = match.group()
        return word
    else:
        return None


