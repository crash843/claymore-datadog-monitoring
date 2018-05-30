import time
import datetime
import json

import requests

CLIENT_ID = ''
CLIENT_SECRET = ''
USERNAME = ''
PASSWORD = ''

AUTH_URL = 'https://api.netatmo.com/oauth2/token'
STATION_URL = 'https://api.netatmo.com/api/getstationsdata'


class ClientAuth:
    def __init__(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                 username=USERNAME, password=PASSWORD, scope='read_station'):

        self.client_id = client_id
        self.client_secret = client_secret

        resp = requests.post(
            AUTH_URL, data={
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': username,
                'password': password,
                'scope': scope
        }).json()
        print(resp)

        self._access_token = resp['access_token']
        self.refresh_token = resp['refresh_token']
        self.scope = resp['scope']
        self.expiration = int(resp['expire_in'] + time.time())

    @property
    def access_token(self):

        if self.expiration < time.time():
            resp = requests.post(
                AUTH_URL, data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
            }).json()
            self._access_token = resp['access_token']
            self.refresh_token = resp['refresh_token']
            self.expiration = int(resp['expire_in'] + time.time())
        return self._access_token


class WeatherStation:
    def __init__(self):
        self.auth = None
        self.refresh_time = 10 * 60 + 30
        self.data = {}

    def get_outdoor_data(self):
        last_updated = lambda: time.time() - self.data['dashboard_data']['time_utc']
        if not self.data or last_updated() > self.refresh_time:
            self.data = self.get_raw_data()

        module_data = self.data['modules'][0]['dashboard_data']
        return {
            'updated': datetime.datetime.fromtimestamp(module_data['time_utc']),
            'temperature': module_data['Temperature'],
            'humidity': module_data['Humidity'],
        }

    def get_raw_data(self):
        return requests.post(
            STATION_URL, data={
                'access_token': self.access_token,
        }).json()['body']['devices'][0]

    @property
    def access_token(self):
        if not self.auth:
            self.auth = ClientAuth()
        return self.auth.access_token


weather_station = WeatherStation()

def get_metrics_data():
    outdoor_data = weather_station.get_outdoor_data()
    metrics = [
        {
            'metric': 'environment.temperature',
            'points': outdoor_data['temperature'],
            'type': 'gauge',
        },
        {
            'metric': 'environment.humidity',
            'points': outdoor_data['humidity'],
            'type': 'gauge',
        },
    ]
    return metrics