from random import randint
import pandas as pd
import numpy as np
import os
from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta as tDelta

os.path.realpath(__file__)
scriptDirectory = os.path.dirname(os.path.realpath(__file__))
df = pd.read_csv('Admission_Predict_Ver1.1.csv')
df.keys()