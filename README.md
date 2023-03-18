# mariafm
Get scrobbles from last.fm and push them into a mariadb database

## Overview:
This python script copies the scrobbles of a user into a mariadb database for further data analysis.
The information stored:
 - Artist
 - Album
 - Track
 - Scrobbled

### Requirements
The required python packages can be installed via `pip install -r requirements.txt`

## Setup:
### Last.fm API Key:
 - You need your own last.fm API key which you can request at [last.fm API](https://www.last.fm/api "last.fm API")
 - Once youo got your last.fm API key, add it to the mariafm.py file

### Database:
 - You should setup your own database first. Then you can use the provided sql dump to create the lastfm table to store the information in. 
 - Once setup, you need to adjust the mariafm.py file to connect to your database

### Issues:
Currently only the last 200 scrobbles are compared and pulled into the database. This is due to the recent_tracks api call is limited to 200 scrobbles. This shoudl be enough to have the script setup as a cron every night. It can also be run manually should you listen to a lot of music.
