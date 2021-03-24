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
list_upper = [x.upper() for x in list_cut_pun]
list_upper_2 = [x.replace('-', ' - ') for x in list_upper]
split_list = [x.split() for x in list_upper_2]
sorted_split = [sorted(x) for x in split_list]

# converts list to string to allow for counting
def listToString(s):
    str1 = " "

    return (str1.join(s)[1:])


joined_sorted = [listToString(x) for x in sorted_split]


# Unique counter for first iteration, counts the number of unique song matches

total_i = {}


def unique_counter(list_of_songs):
    for i in range(len(list_of_songs)):
        song = list_of_songs[i]

        if song in total_i:
            total_i[song] += 1
            continue

        best_match = None
        best_ratio = 0

        for key in total_i.keys():
            match_ratio = SequenceMatcher(a=song, b=key).ratio()
            if match_ratio >= 0.6 and match_ratio >= best_ratio:
                best_ratio = match_ratio
                best_match = key

        if best_ratio >= 0.6 and best_match:
            total_i[best_match] += 1
            continue

        total_i[song] = 1

unique_counter(joined_sorted)


#First iteration dictionary (HtL)
{k: v for k, v in sorted(total_i.items(), key=lambda item: item[1], reverse=True)}

total_2i = total_i

for key in list(total_i):
    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = "https://api.spotify.com/v1/search"
    data = urlencode({"q": key, "type": "playlist"})
    lookup_url = f"{endpoint}?{data}"
    req = requests.get(lookup_url, headers=headers)

    if (len(req.json().get('playlists').get('items'))) <= 1:
        continue
    else:
        description_list_2i = [x.get('description') for x in req.json().get('playlists').get('items')]
        split_2i = [split_chooser(x) for x in description_list_2i]
        splitlist_2i = sum(split_2i, [])
        list_1_2i = list(filter(lambda title: dash_finder(title), splitlist_2i))
        list_cut_2i = [colon_cutter(x) for x in list_1_2i]
        list_cut_pun_2i = [punc_remover(x) for x in list_cut_2i]
        list_upper_2i = [x.upper() for x in list_cut_pun_2i]
        list_upper_2_2i = [x.replace('-', ' - ') for x in list_upper_2i]
        split_list_2i = [x.split() for x in list_upper_2_2i]
        sorted_split_2i = [sorted(x) for x in split_list_2i]
        joined_sorted_2i = [listToString(x) for x in sorted_split_2i]

        for i in range(len(joined_sorted_2i)):
            song = joined_sorted_2i[i]

            if song in total_2i:
                total_2i[song] += 1
                continue

            best_match = None
            best_ratio = 0

            for key_2 in total_2i.keys():
                match_ratio = SequenceMatcher(a=song, b=key_2).ratio()
                if match_ratio >= 0.6 and match_ratio >= best_ratio:
                    best_ratio = match_ratio
                    best_match = key_2

            if best_ratio >= 0.6 and best_match:
                total_2i[best_match] += 1
                continue

            total_2i[song] = 1