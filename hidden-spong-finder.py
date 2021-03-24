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


#Spotify API access details

client_id = '7161d3c861074d91ba1a3295c735d249'
client_secret = 'c223f0bf1d674c2ea288fc049bc096f8'