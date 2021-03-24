#Imports
from bs4 import BeautifulSoup
import requests
import base64
import datetime
from urllib.parse import urlencode
import json
from itertools import chain
import numpy as np
import pandas as pd
from difflib import SequenceMatcher


######## Enter song here within the "" ########
song_to_search = "Pulse - Showdown"


#Spotify API access details

client_id = '7161d3c861074d91ba1a3295c735d249'
client_secret = 'c223f0bf1d674c2ea288fc049bc096f8'


# Getting access token for Spotify API

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True


client = SpotifyAPI(client_id, client_secret)
client.perform_auth()


#Searches via Spotify API
access_token = client.access_token
headers = {"Authorization": f"Bearer {access_token}"}
endpoint = "https://api.spotify.com/v1/search"
data = urlencode({"q": song_to_search, "type": "playlist"})
print(data)

lookup_url = f"{endpoint}?{data}"
print(lookup_url)
r = requests.get(lookup_url, headers=headers)
print(r.status_code)