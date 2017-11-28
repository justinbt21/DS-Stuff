# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 17:57:00 2017

@author: justintran
"""

import pandas as pd
import numpy as np
import nba_py as nba
from nba_py import player
import webscrape

# Params
p_year = '2017-18'
FantasyTeam = ['john wall', 'rudy gobert', 'lonzo ball', 'khris middleton', 'jj redick', 'aaron gordon', 'andre drummond', 'darren collison', 'will barton', 'markieff morris', 'joe ingles', 'jamychal green', 'dewayne dedmon']


AllCurrentPlayers = pd.DataFrame(player.PlayerList('00', season = p_year, only_current = 1).info())
AllPlayerIds = AllCurrentPlayers['PERSON_ID']


CurrentStats = pd.DataFrame(None)
for i in range(0, len(AllPlayerIds)-1):

    result = pd.DataFrame(player.PlayerCareer(AllPlayerIds[i], 'PerGame', '00').regular_season_totals())
    result = result.loc[result['SEASON_ID'] == p_year]
    # player_name = AllCurrentPlayers.loc[AllCurrentPlayers['PERSON_ID'] == result['PLAYER_ID'].item()]['DISPLAY_FIRST_LAST']
    # result = result.set_index(player_name.index)
    # result['PLAYER_NAME'] = player_name
    CurrentStats = CurrentStats.append(result)
    print(i)
    
CurrentStats = pd.merge(CurrentStats, AllCurrentPlayers[['PERSON_ID','DISPLAY_FIRST_LAST']], how='left', left_on = 'PLAYER_ID', right_on = 'PERSON_ID')

player.PlayerGameLogs(webscrape.getPlayerId('lonzo ball').item(), '00', '2017-18', 'Regular Season').info()