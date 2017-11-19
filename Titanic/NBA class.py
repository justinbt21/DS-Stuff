# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 12:05:09 2017

@author: justintran
"""

import pandas as pd
import numpy as np
from nba_py import player
import importlib


def getPID(name):
    name = name.split(' ')
    pid = player.get_player(name[0], name[1], just_id = True).item()
    return pid

def getData(name, *start_year):
    id = getPID(name)
    
    df = pd.DataFrame(player.PlayerCareer(id, 'PerGame').regular_season_totals())
    df.columns = list(map(lambda x:x.lower(), df))
    
    if start_year[0]:
        year = str(start_year[0]) + '-' + str(start_year[0]+1)[-2:]
        df = df.loc[df['season_id'] == year]
        
    return df

