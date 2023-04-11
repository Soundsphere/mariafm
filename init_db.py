#!/usr/bin/env python3

import json
import requests
import mariadb
from datetime import datetime
import time
import pytz
import config
import pandas as pd


## last.fm API key and username
apikey = config.lastfm_apikey
## username is user_name to keep it separate from the database column Username
user_name = config.user_name

## connect to the database
conn = mariadb.connect(
    user=config.user,
    password=config.password,
    host=config.host,
    database=config.database)
cur = conn.cursor()


## set the date/time with the correct timezone. change it for yours if needed
def date_form_tz(datevalue):
    datestring = datevalue
    datetime = pd.to_datetime(datestring, utc=True)
    date_out = datetime.astimezone(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%dT%H:%M:%S')
    return(date_out)
    

## this gets us the lastfm recent tracks for the page number
response = requests.get('https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + user_name + '&api_key=74a64595e8af72194dfd790c36dc83d8&format=json')
recents = json.loads(response.text)


## get all tracks from lastfm in starting from the last page
totalp = int((recents['recenttracks']['@attr']['totalPages']))
allrecent = []
page = 1
while page <= totalp:
    allrec = requests.get('https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + user_name + '&api_key=74a64595e8af72194dfd790c36dc83d8&page=' + str(totalp) + '&format=json')
    alltherecdata = json.loads(allrec.text)
    if '@attr' in alltherecdata['recenttracks']['track'][0]:
        for items in alltherecdata['recenttracks']['track'][1:]:
            allrecent.append((items['name'],items['artist']['#text'],items['album']['#text'],date_form_tz(items['date']['#text'])))
    else:
        for items in alltherecdata['recenttracks']['track']:
            allrecent.append((items['name'],items['artist']['#text'],items['album']['#text'],date_form_tz(items['date']['#text'])))
    print(allrecent)
    print("\nPage: " + str(totalp) + "\n")
    totalp -= 1


## get the loved tracks from last.fm. This call gets us the page number of loved tracks to iterate over
response = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user=' + user_name + '&api_key=' + apikey + '&format=json')
loved = json.loads(response.text)


## get the actual loved tracks and store them in a list
totalp = (loved['lovedtracks']['@attr']['totalPages'])
lovedtracks = []
page = 1
while page <= int(totalp):
    response = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getlovedtracks&user=' + user_name + '&api_key=' + apikey + '&' + str(page) + '&format=json')
    allthedata = json.loads(response.text)
    for items in allthedata['lovedtracks']['track']:
        lovedtracks.append((items['name']+ ",", items['artist']['name']))
    page += 1


for item in allrecent:
	if (item[0] + ",", item[1]) in lovedtracks:
		cur.execute('INSERT INTO lastfm (Username,Track,Artist,Album,Loved,Scrobbled) VALUES (?, ?, ?, ?, ?, ?)', (user_name, item[0], item[1], item[2], "true", item[3]))
	else:
		cur.execute('INSERT INTO lastfm (Username,Track,Artist,Album,Loved,Scrobbled) VALUES (?, ?, ?, ?, ?, ?)', (user_name, item[0], item[1], item[2], "false", item[3]))
conn.commit()


## close connection and be done with it
conn.close()