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


#Checks number of playlists
len(r.json().get('playlists').get('items'))


description_list = [x.get('description') for x in r.json().get('playlists').get('items')]


# Chooses what item divides tracks and splits by it
def split_chooser(descr):
    num1 = descr.count('&#x2F;&#x2F')
    num2 = descr.count('|')
    num3 = descr.count(',')
    num4 = descr.count('│')
    num5 = descr.count('&#x2F')
    num6 = descr.count(' l ')

    if (num1 >= num2) and (num1 >= num3) and (num1 >= num4) and (num1 >= num5) and (num1 >= num6):
        return descr.split('&#x2F;&#x2F')
    elif (num2 >= num1) and (num2 >= num3) and (num2 >= num4) and (num2 >= num5) and (num2 >= num6):
        return descr.split('|')
    elif (num3 >= num1) and (num3 >= num2) and (num3 >= num4) and (num3 >= num5) and (num3 >= num6):
        return descr.split(',')
    elif (num4 >= num1) and (num4 >= num2) and (num4 >= num3) and (num4 >= num5) and (num4 >= num6):
        return descr.split('│')
    elif (num5 >= num1) and (num5 >= num2) and (num5 >= num3) and (num5 >= num4) and (num5 >= num6):
        return descr.split('&#x2F')
    else:
        return descr.split(' l ')


split = [split_chooser(x) for x in description_list]
splitlist = sum(split, [])

# checks to see if a "-" is present so cuts the non songs
def dash_finder(title):
    if "-" in title.lower():
        return True
    else:
        return False


list_1 = list(filter(lambda title: dash_finder(title), splitlist))

#removes entry before a ':'
def colon_cutter (title):
    if ":" in title:
        return title.split(':')[1]
    else:
        return title

list_cut = [colon_cutter(x) for x in list_1]

# removes punctuation ';' and '.'

def punc_remover(title):
    if ";" or "." in title:
        return title.replace(';', ' ').replace('.', ' ')
    else:
        return title


list_cut_pun = [punc_remover(x) for x in list_cut]
