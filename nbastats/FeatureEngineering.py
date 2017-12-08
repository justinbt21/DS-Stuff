# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 17:57:00 2017

@author: justintran
"""

import pandas as pd
import numpy as np
import nba_py as nba
from nba_py import player
from nba_py import game
from webscrape import getData
from time import sleep

# Params
p_year = '2017'
FantasyTeam = ['john wall', 'rudy gobert', 'lonzo ball', 'khris middleton', 'jj redick', 'aaron gordon', 'andre drummond', 'darren collison', 'will barton', 'markieff morris', 'joe ingles', 'josh richardson', 'dewayne dedmon']

playerInfo = pd.DataFrame(player.PlayerList(season='2017-18', only_current=1).info())
"""
def tradeMachine(current_team, proposed_players, receiving players, season=2017):
    df = pd.DataFrame()
    for i in current_team:
        data = getData(i, 'PerGame', season)
        data['PLAYER_NAME'] = i.title()
        df = df.append(data)
        sleep(3)
    return df

"""

    
# CurrentStats = pd.merge(CurrentStats, AllCurrentPlayers[['PERSON_ID','DISPLAY_FIRST_LAST']], how='left', left_on = 'PLAYER_ID', right_on = 'PERSON_ID')

def combineTeam(name, season):
    df = getData(name, 'gamelog', season)
    df.columns = [x.upper() for x in df.columns]
    sleep(2)
    pid = df['PLAYER_ID'].unique()[0]
    df['TEAM_ID'] = playerInfo['TEAM_ID'].loc[playerInfo['PERSON_ID'] == pid].item()
    total = df['GAME_ID'].count()
    counter = 0
    ts = pd.DataFrame()
    for i in df['GAME_ID']:
        teamstats = pd.DataFrame(game.Boxscore(str(i), str(season) + '-' + str(int(season)+1)[-2:]).team_stats())
        teamstats.columns = ['TEAM_'+str(x) for x in teamstats.columns]
        ts = ts.append(teamstats)
        sleep(2)
        counter += 1
        print('Finished {0} %'.format(round((counter/total)*100,0)))
    
    df = pd.merge(df, ts, how='left', left_on=['GAME_ID'], right_on = ['TEAM_GAME_ID'])
    # Player Stats and Team Stats
    df1 = df.loc[df['TEAM_ID'] == df['TEAM_TEAM_ID']] 
    df1 = df1.drop(['VIDEO_AVAILABLE', 'TEAM_GAME_ID', 'TEAM_TEAM_ID'], axis=1)
    df1 = df1.rename(columns = {'TEAM_TEAM_NAME' : 'TEAM_NAME', 'TEAM_TEAM_ABBREVIATION' : 'TEAM_ABBREVIATION', 'TEAM_TEAM_CITY' : 'TEAM_CITY'})
    # Opposing Team Stats
    df2 = df.loc[df['TEAM_ID'] != df['TEAM_TEAM_ID']].iloc[:,27:]
    df2 = df2.rename(columns = {'TEAM_TEAM_NAME' : 'TEAM_NAME', 'TEAM_TEAM_ABBREVIATION' : 'TEAM_ABBREVIATION', 'TEAM_TEAM_CITY' : 'TEAM_CITY'})
    df2.columns = ['OPP_'+x for x in df2.columns]
    df2 =  df2.drop('OPP_TEAM_ID', axis = 1)
    
    df = pd.merge(df1, df2, 'left', left_on='GAME_ID', right_on='OPP_TEAM_GAME_ID')
    return df