# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:05:09 2017

@author: justintran
"""

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from lxml import html
import requests
import urllib3
import pandas as pd
import nba_py as nba
from nba_py import player
import sys


def getPID(name):
    name = name.split(' ')
    pid = player.get_player(name[0], name[1], just_id = True).item()
    return pid

def makeSoup(url):
	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	       'Accept-Encoding': 'none',
	       'Accept-Language': 'en-US,en;q=0.8',
	       'Connection': 'keep-alive'}
	http = urllib3.PoolManager()
	page = http.request('GET', url)
	content = page.data

	soup = BeautifulSoup(content, 'lxml')
	return soup


def makeHeaders(soup):

	column_headers = [th.getText() for th in soup.findAll('th')]
	return  column_headers

def makeDataframe(soup):

	column_headers = makeHeaders(soup)
	data_rows = soup.findAll('tr')[1:]
	player_data = [[td.getText() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))]

	df = pd.DataFrame(player_data, columns=column_headers)
	return df


def getPlayerId(name):
    name = name.split(' ')

    # If returned with execption 400 bad request for url, you sometimes have to open the link in your browser then it will work. Weird bug.

    player = nba.player.get_player(name[0], name[1], just_id=True)
    return player

def getURL(id, season):

	id = str(int(id))
	url ='http://nbasavant.com/ajax/getShotsByPlayer.php?hfST=&hfQ=&pid%5B%5D='+id+'&hfSZB=&hfSZA=&hfSZR=&ddlYear='+season+'&txtGameDateGT=&txtGameDateLT=&ddlGameTimeGT_min=&ddlGameTimeGT_sec=&ddlGameTimeLT_min=&ddlGameTimeLT_sec=&ddlShotClockGT=&ddlShotClockLT=&ddlDefDistanceGT=&ddlDefDistanceLT=&ddlDribblesGT=&ddlDribblesLT=&ddlTouchTimeGT=&ddlTouchTimeLT=&ddlShotDistanceGT=&ddlShotDistanceLT=&ddlTeamShooting=&ddlTeamDefense=&hfPT=&ddlGroupBy=player&ddlOrderBy=shots_made_desc&hfGT=0%7C&ddlShotMade=&ddlMin=0&player_id='+id+'&data=null&_=1459806001585'
    
	return url

def getData(name, season, type):
	if type == 'ShotDist':
		id = getPlayerId(name)
		url = getURL(id, str(season))
		soup = makeSoup(url)
		df = makeDataframe(soup)
		return df
	
	elif type == 'PerGame':
		id = getPlayerId(name)
		df = pd.DataFrame(player.PlayerCareer(id, 'PerGame').regular_season_totals())
		df.columns = list(map(lambda x:x.lower(), df))

		if season:
			year = season + '-' + str(int(season)+1)[-2:]
			df = df.loc[df['season_id'] == year]
		return df

	elif type == 'GameLogs':
		id = getPlayerId(name)
		year = season + '-' + str(int(season)+1)[-2:]
		df = player.PlayerGameLogs(getPlayerId(id), '00', year, 'Regular Season').info()
		df['GAME_DATE'] = pd.to_datetime(pd.to_datetime(df['GAME_DATE'], infer_datetime_format = True), format= '%Y%m%d')
		return df
		
