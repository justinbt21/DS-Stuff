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
p_year = '2017'
FantasyTeam = ['john wall', 'rudy gobert', 'lonzo ball', 'khris middleton', 'jj redick', 'aaron gordon', 'andre drummond', 'darren collison', 'will barton', 'markieff morris', 'joe ingles', 'jamychal green', 'dewayne dedmon']


AllCurrentPlayers = pd.DataFrame(player.PlayerList('00', season = p_year + '-' + str(int(p_year)+1)[-2:], only_current = 1).info())

CurrentStats = pd.DataFrame(None)
for i in range(0, len(FantasyTeam)-1):

    result = webscrape.getData(FantasyTeam[i], 'PerGame', p_year)
    # player_name = AllCurrentPlayers.loc[AllCurrentPlayers['PERSON_ID'] == result['PLAYER_ID'].item()]['DISPLAY_FIRST_LAST']
    # result = result.set_index(player_name.index)
    # result['PLAYER_NAME'] = player_name
    CurrentStats = CurrentStats.append(result)

print('Done')
    
# CurrentStats = pd.merge(CurrentStats, AllCurrentPlayers[['PERSON_ID','DISPLAY_FIRST_LAST']], how='left', left_on = 'PLAYER_ID', right_on = 'PERSON_ID')

