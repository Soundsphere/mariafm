# mariafm
Get scrobbles from last.fm and push them into a mariadb database

## Overview:
This python script copies the scrobbles of a user into a mariadb database for further data analysis.
The information stored:
 - Track
 - Artist
 - Album
 - Loved
 - Scrobbled

### Requirements
The required python packages can be installed via `pip install -r requirements.txt`

## Setup:
### Last.fm Setup
 - You need your own last.fm API key which you can request at [last.fm API](https://www.last.fm/api "last.fm API")
 - Once you got your last.fm API key, add it to the mariafm.py file
 - Add your username to the mariafm.py file

### Database:
 - You should setup your own database first. Then you can use the provided sql dump to create the lastfm table to store the information in. 
 - Once setup, you need to adjust the mariafm.py file to connect to your database

### Things to keep in mind:
Currently only the last 4 pages of recent scrobbles are checked against the database. This equates to 200 scrobbles, which should be plenty for now. 
Since I also run the script in a cronjob every 24h, this should be enough to keep the database in sync with lastfm. 