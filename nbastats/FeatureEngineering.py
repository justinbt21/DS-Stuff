# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 17:57:00 2017

@author: justintran
"""

from random import randint
import pandas as pd
import numpy as np
import nba_py as nba
from nba_py import player
from nba_py import game
from webscrape import getData
from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta as tDelta
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

# Params
current_year = int(datetime.date(datetime.now()).strftime('%Y'))-1 if datetime.date(datetime.now()).month < 11 else int(datetime.date(datetime.now()).strftime('%Y'))
fantasy_team = ['john wall', 'rudy gobert', 'lonzo ball', 'khris middleton', 'jj redick', 'aaron gordon', 'andre drummond', 'darren collison', 'will barton', 'markieff morris', 'joe ingles', 'josh richardson', 'dewayne dedmon']
trade_for = ['kyle lowry', 'thaddeus young']
trading = ['john wall', 'jj redick']

<<<<<<< HEAD
playerInfo = pd.DataFrame(player.PlayerList(season='2017-18', only_current=1).info())
"""
def tradeEvaluator(current_team, proposed_players, receiving_players, season=2017):
    df = pd.DataFrame()
    for i in current_team:
        data = getData(i, 'GameLog', season)
        data['PLAYER_NAME'] = i.title()
        df = df.append(data)
        sleep(3)

    for i in receiving_players:
    	data = getData(i, 'GameLog', season)
    	data['PLAYER_NAME'] = i.title()
    	df = df.append(data)
    	sleep(3)

    mean = pd.DataFrame(df.groupby('PLAYER_NAME').mean.())
	std = pd.DataFrame(df.groupby('PLAYER_NAME').std())
	stats = pd.merge(mean, std, how = 'inner', on = 'PLAYER_NAME')
	df = pd.merge(df, stats, how = 'inner', on = 'PLAYER_NAME')
=======
playerInfo = pd.DataFrame(player.PlayerList(season=str(current_year)+'-'+str(int(current_year)+1)[-2:], only_current=1).info())

def getStats(player_list, season=current_year, last_game_range = None):
    df = pd.DataFrame()
    for i in player_list:
        print(i.title())
        data = getData(i, 'GameLog', season)
        if last_game_range:
            data = data.sort_values('GAME_DATE')
            data = data.loc[data.GAME_DATE >= datetime.date(datetime.now()) - tDelta(days=+last_game_range)]
            data['PLAYER_NAME'] = i.title()
            df = df.append(data)
            sleep(randint(1,3))
            continue
        
        data['PLAYER_NAME'] = i.title()
        df = df.append(data)
        sleep(randint(1,3))

>>>>>>> master
    return df


def tradeEvaluator(current_team, proposed_players=[], received_players=[], season=current_year, last_game_range = None, graph_data = False):
    total_players = fantasy_team + received_players

    df = getStats(total_players, season, last_game_range = last_game_range)

    current_team = df.loc[df['PLAYER_NAME'].str.lower().isin(fantasy_team)]
    new_team = df.loc[~df['PLAYER_NAME'].str.lower().isin(proposed_players)]

    current_stats = current_team.groupby('PLAYER_NAME').mean() * 3
    current_total_stats = current_stats.sum()
    current_total_stats['FG_PCT'] = current_total_stats['FGM']/current_total_stats['FGA']
    current_total_stats['FG3_PCT'] = current_total_stats['FG3M']/current_total_stats['FG3A']
    current_total_stats['FT_PCT'] = current_total_stats['FTM']/current_total_stats['FTA']
    
    new_stats = new_team.groupby('PLAYER_NAME').mean() * 3
    new_total_stats = new_stats.sum()
    new_total_stats['FG_PCT'] = new_total_stats['FGM']/new_total_stats['FGA']
    new_total_stats['FG3_PCT'] = new_total_stats['FG3M']/new_total_stats['FG3A']
    new_total_stats['FT_PCT'] = new_total_stats['FTM']/new_total_stats['FTA']

    drop_cols = ['VIDEO_AVAILABLE', 'Player_ID', 'PLUS_MINUS', 'MIN', 'PF', 'FGM', 'FGA', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'OREB', 'DREB']
    trade_eval_stats = new_total_stats - current_total_stats
    trade_eval_stats = trade_eval_stats.drop(drop_cols)
    current_total_stats = current_total_stats.drop(drop_cols)
    
    pct_change_stats = trade_eval_stats / current_total_stats
    
    df1 = pd.DataFrame(trade_eval_stats, columns = ['Weekly Change'])
    df2 = pd.DataFrame(pct_change_stats, columns = ['Percent Change'])
    
    chart = df1.merge(df2, 'inner', left_index = True, right_index = True)
    graph_bar = [go.Bar(
            x = list(pd.DataFrame(pct_change_stats).reset_index()['index']),
            y = list(pct_change_stats.round(3))
        )]
    layout = {
                'xaxis': {'title': '% Change'},
                'yaxis': {'title': 'Fantasy Category'},
                'barmode': 'relative',
                'title' : 'Trade Evaluator'
            }

    bar = plot({'data': graph_bar, 'layout': layout})
    
    data = bar if graph_data == True else chart

    return data


def combineTeam(name, season=current_year):
    df = getData(name, 'gamelog', season)
    sleep(1)
    df.columns = [x.upper() for x in df.columns]
    pid = df['PLAYER_ID'].unique()[0]
    df['TEAM_ID'] = playerInfo['TEAM_ID'].loc[playerInfo['PERSON_ID'] == pid].item()
    total = df['GAME_ID'].count()
    counter = 0
    ts = pd.DataFrame()
    for i in df['GAME_ID']:
        teamstats = pd.DataFrame(game.Boxscore(str(i), str(season) + '-' + str(int(season)+1)[-2:]).team_stats())
        teamstats.columns = ['TEAM_'+str(x) for x in teamstats.columns]
        ts = ts.append(teamstats)
        sleep(randint(1,3))
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
    df = df.drop('OPP_TEAM_GAME_ID', axis=1)
    return df