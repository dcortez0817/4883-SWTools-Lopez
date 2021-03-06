"""
Course: cmps 4883
Assignemt: A03
Date: 2/05/19
Github username: JakobLopez
Repo url: https://github.com/JakobLopez/4883-SWTools-Lopez
Name: Jakob Lopez
Description: 
    NFL provides JSON data that contains detailed game information
    for every single game played. This program collects every JSON
    item for each game from 2009 to 2018 and places them in a folder.
    Using knowledge of the NFL website URL, the game-id for every game
    is collected and used to access the JSON items
"""
from beautifulscraper import BeautifulScraper
from pprint import pprint
import json
import urllib
import requests
import sys

scraper = BeautifulScraper()

#Years 2009 to 2018
years = list(range(2009, 2019))

#Week 1 to 17
weeks = list(range(1,18))

#Dictionary of REG & POST keys that have list values 
gameIDs = {
    'REG': [],
    'POST': []
}

#Opens a file for writing
f = open("gameIDs.json","w")

"""
Name: scrape_data
Description: 
    Gets gameID for every game on url page.
    Uses gameID to access game data.
    Writes. every game to a folder
    Write every game ID to dictionary under its season type
Params:
    year - year to get gameIDs from
    stype - season type: REG or POST
    week - week to get gameIDs from (only for REG season)
Returns:
    Nothing, but does add game IDs to global dictionary
"""
def scrape_data(year, stype, week = None):
    #URL is different depending on season type
    if stype == 'POST':
        url = 'http://www.nfl.com/schedules/%d/%s' % (year,stype)
    else:
        url = 'http://www.nfl.com/schedules/%d/%s%s' % (year,stype,str(week))

    #Go to URL
    page = scraper.go(url)

    #Get list of div tags where 'class' = 'schedules-list-content'
    divs = page.find_all('div',{'class':'schedules-list-content'})
    #Loops through every game on page
    for div in divs:
        #Ignore pro bowl
        if div['data-away-abbr'] in ['APR', 'NPR', 'AFC', 'NFC', 'IRV', 'RIC', 'CRT', 'SAN']:
            pass
        else:
            gameIDs[stype].append(div['data-gameid'])
            #URL to json game data
            url = 'http://www.nfl.com/liveupdate/game-center/%s/%s_gtd.json' % (div['data-gameid'],div['data-gameid'])
            #Write to folder
            #Each file named gameid.json
            urllib.request.urlretrieve(url, 'game_data/'+div['data-gameid']+'.json')

#Loop through NFL years
for year in years:
    scrape_data(year, 'POST')
    #Loop through REG season weeks each year
    for week in weeks:
        scrape_data(year, 'REG', week)
    

#Writes all game IDs
f.write(json.dumps(gameIDs))
