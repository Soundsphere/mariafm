#!/usr/bin/env python3

## script to get the latest scrobbles from last.fm and import them into my mariadb database
## the last 200 scrobbles from the database and lastfm are compared and the difference that is not
## in the database will be added. 200 is the upper limit the lastfm api will allow, but it should
## be enough since I rarely listen to more than 200 scrobbles a day anyway. 

## TODO: 
## Once a track is loved, all tracks in the database should be set to true as well
## UPDATE Stuff.lastfm SET Loved = 'true' WHERE Track = 'RecentlyLovedTrackname'
## with this everything is kept in sync. 
## To see when the track was loved we can include the date from lovedtracks api
## -> or keep tracks the way they are and only add loved = true going forward?



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


## get the amount of records from the database based on the pages to iterate over set in the config file
## if the pages in the config are set to 4, then 200 records are compared
def page_iterate():
    recent_page = (int(config.pages) * 50)
    return(int(recent_page))


## Get the last n records scrobbled tracks from the database based on the config.pages set
cur.execute('SELECT Track, Artist, Album, Scrobbled FROM Stuff.lastfm ORDER BY Scrobbled DESC LIMIT ' + str(page_iterate()))
mariabase = []
for Track,Artist,Album,Scrobbled in cur: 
     mariabase.append((Track, Artist, Album, date_form(Scrobbled)))


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
        lovedtracks.append((items['name'] + ",", items['artist']['name']))
    page += 1


## get the last n pages of scrobbles from last.fm based on the amount of pages set in the config file
page = 1
lastscrobbles = []
while page <= int(config.pages):
    response = requests.get('http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=' + user_name + '&api_key=' + apikey + '&page=' + str(page) + '&format=json')
    data = json.loads(response.text)
    if '@attr' in data['recenttracks']['track'][0]:
        for items in data['recenttracks']['track'][1:]:
            lastscrobbles.append((items['name'],items['artist']['#text'],items['album']['#text'],date_form_tz(items['date']['#text'])))
    else:
        for items in data['recenttracks']['track']:
            lastscrobbles.append((items['name'],items['artist']['#text'],items['album']['#text'],date_form_tz(items['date']['#text'])))
    page += 1


## change to sets and compare the two, gives me the difference missing in the database
datadiff = set(lastscrobbles) - set(mariabase)


## if the set is blank, skip adding the info. If there's something in the set, iterate over the items and add them to the database
## and give me a nice-ish output of what has been added
if not datadiff:
    print('No new scrobbles to add')
else: 
    for item in datadiff:
        if (item[0] + ",", item[1]) in lovedtracks:
            cur.execute('INSERT INTO lastfm (Username,Track,Artist,Album,Loved,Scrobbled) VALUES (?, ?, ?, ?, ?, ?)', (user_name, item[0], item[1], item[2], "true", item[3]))
        else:
            cur.execute('INSERT INTO lastfm (Username,Track,Artist,Album,Loved,Scrobbled) VALUES (?, ?, ?, ?, ?, ?)', (user_name, item[0], item[1], item[2], "false", item[3]))
    conn.commit()
    count_added = 1
    for added in datadiff:
        print(str(count_added) + '. - ', added[0] + ",", added[1] + ",", added[2] + ",", added[3])
        count_added += 1


## close connection and be done with it
conn.close()