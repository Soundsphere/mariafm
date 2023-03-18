#!/usr/bin/env python3

## script to get the latest scrobbles from last.fm and import them into my mariadb database
## the last 200 scrobbles from the database and lastfm are compared and the difference that is not
## in the database will be added. 200 is the upper limit the lastfm api will allow, but it should
## be enough since I rarely listen to more than 200 scrobbles a day anyway. 

import json
import requests
import mariadb
from datetime import datetime
import time
import pytz
import pandas as pd


## your last.fm API key and username
apikey = 'your_api_key'
username = 'your username'

## connect to the database
conn = mariadb.connect(
    user='username',
    password='password',
    host='serverip',
    database='database')
cur = conn.cursor() 


## change the date format so that it can be inserted into the database. It also applies a timezone
## this is needed as last.fms api gives me the times in UTC, therefore it's off by an hour during winter and 
## two during summer. This function changes the date to Europe/Berlin
def date_form_tz(datevalue):
    datestring = datevalue
    datetime = pd.to_datetime(datestring, utc=True)
    date_out = datetime.astimezone(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%dT%H:%M:%S')
    return(date_out)
    

## change the date without the timezone so that the database inputs can be direclty compared to the last.fm dates
## Since the database has the correct values already, there's no need to apply a timezone again. 
def date_form(datevalue):
    datestring = datevalue
    datetime = pd.to_datetime(datestring)
    date_out = datetime.strftime('%Y-%m-%dT%H:%M:%S')
    return(date_out)


## Get the last 200 scrobbled tracks from the database
cur.execute('SELECT Artist, Album, Track, Scrobbled FROM Stuff.lastfm ORDER BY Scrobbled DESC LIMIT 200') 
mariabase = []
for Artist,Album,Track,Scrobbled in cur: 
     mariabase.append((Artist, Album, Track, date_form(Scrobbled)))


## get the last 200 scrobbles from lastfm as well. Skip the first iteration should the nowplaying tag be in the json so that the current played track is not added to the database
response = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + username + '&api_key=' + apikey + '&format=json&extended=0&limit=200')
data = json.loads(response.text)
lastfm = []
if '@attr' in data['recenttracks']['track'][0]:
    for items in data['recenttracks']['track'][1:]:
        lastfm.append((items['artist']['#text'],items['album']['#text'],items['name'],date_form_tz(items['date']['#text'])))
else:
    for items in data['recenttracks']['track']:
        lastfm.append((items['artist']['#text'],items['album']['#text'],items['name'],date_form_tz(items['date']['#text'])))


## change to sets and compare the two, gives me the difference missing in the database
datadiff = set(lastfm) - set(mariabase)

## if the set is blank, skip adding the info. If there's something in the set, iterate over the items and add them to the database
if not datadiff:
    print('No new scrobbles to add')
else: 
    for item in datadiff:
        cur.execute('INSERT INTO lastfm (UserName,Artist,Album,Track,Scrobbled) VALUES (?, ?, ?, ?, ?)', (username, item[0], item[1], item[2], item[3]))
    print('new scrobbles addeds to the database')
    conn.commit()

## close connection and be done with it
conn.close()