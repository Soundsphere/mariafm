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
 - Once you got your last.fm API key, add it to the config.py file
 - Add your username to the config.py file

### Database:
 - You should setup your own database first. Then you can use the provided sql dump to create the lastfm table to store the information in. 
 - Once setup, you need to adjust the config.py file to connect to your database, by adding database, username, password and server

### Pages:
 - In the config file you can set the pages to iterate over in last.fm. One recent tracks page shows 50 tracks, so if you set the pages to 6, you'll get 300 tracks
 - The amount of tracks to get from the database to compare to is based on the page numbers set in the config.py file