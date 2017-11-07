# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 15:41:13 2017

@author: justintran
"""

# Load in our libraries
import pandas as pd
import numpy as np
import re
import sklearn
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt

from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')

import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.graph_objs as go
import plotly.tools as tls

import warnings
warnings.filterwarnings('ignore')

# Going to use these 5 base models for the stacking
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.cross_validation import KFold;

# Load in the train and test datasets
train = pd.read_csv('Titanic/Data/train.csv')
test = pd.read_csv('Titanic/Data/test.csv')

PassengerId = test['PassengerId']
full_data = [train,test]

# Engineered Features

# Length of Name
train['name_length'] = train['Name'].apply(len)
train['name_length'] = test['Name'].apply(len)

# Has Cabin
train['has_cabin'] = train['Cabin'].apply(lambda x: 0 if type(x) == float else 1)
test['has_cabin'] = test['Cabin'].apply(lambda x: 0 if type(x) == float else 1)

# Family Size
for dataset in full_data:
    dataset['family_size'] = dataset['SibSp'] + dataset['Parch'] + 1
    
# IsAlone
for dataset in full_data:
    dataset['is_alone'] = 0
    dataset.loc[dataset['family_size'] == 1, 'is_alone'] = 1
    
# Remove all NULLS in the Embarked column
for dataset in full_data:
    dataset['Embarked'] = dataset['Embarked'].fillna('S')
    
# Remove all NULLS iun the Fare column and create a new feature CategoricalFare
for dataset in full_data:
    dataset['Fare'] = dataset['Fare'].fillna(train['Fare'].median())
train['categorical_fare'] = pd.qcut(train['Fare'], 4, labels = [0,1,2,3])

# Categorical Age
for dataset in full_data:
    age_avg = dataset['Age'].mean()
    age_std = dataset['Age'].std()
    age_null_count = dataset['Age'].isnull().sum()
    age_null_random_list = np.random.randint(age_avg - age_std, age_avg + age_std, size= age_null_count)
    dataset['Age'][np.isnan(dataset['Age'])] = age_null_random_list
train['categorical_age'] = pd.cut(train['Age'], 5, labels = [0,1,2,3,4])

# Title
def get_title(name):
    title_search = re.search(' ([A-Za-z]+)\.', name)
    # If the title exists, extract and return it.
    if title_search:
        return title_search.group(1)
    return ""

for dataset in full_data:
    dataset ['Title'] = dataset['Name'].apply(get_title)

# Group all non-common titles into on single grouping "Rare"
for dataset in full_data:
    dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
    
    dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')


for dataset in full_data:
    
    # Mapping Sex
    dataset['Sex'] = dataset['Sex'].map( {'female': 0, 'male': 1} ).astype(int)
    
    # Mapping titles
    title_mapping = {'Mr': 1, 'Miss': 2, 'Mrs': 3, 'Master': 4, 'Rare': 5}
    dataset['Title'] = dataset['Title'].map(title_mapping)
    dataset['Title'] = dataset['Title'].fillna(0)
    
    #Mapping Embarked
    dataset['Embarked'] = dataset['Embarked'].map( {'S': 0, 'C': 1, 'Q': 2}).astype(int)
    
    #Mapping Fare
    dataset.loc[dataset['Fare'] <= 7.91, 'Fare'] = 0
    dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
    dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare'] = 2
    dataset.loc[(dataset['Fare'] > 14.454), 'Fare'] = 3
    dataset['Fare'] = dataset['Fare'].astype(int)
    
    # Mapping Age
    dataset.loc[ dataset['Age'] <= 16, 'Age'] = 0
    dataset.loc[ (dataset['Age'] > 16) & (dataset['Age'] <= 32), 'Age'] = 1
    dataset.loc[ (dataset['Age'] > 32) & (dataset['Age'] <= 48), 'Age'] = 2
    dataset.loc[ (dataset['Age'] > 48) & (dataset['Age'] <= 64), 'Age'] = 3
    dataset.loc[dataset['Age'] > 64, 'Age'] = 4 ;
    
# Feature selection
drop_elements = ['PassengerId', 'Name', 'Ticket', 'Cabin', 'SibSp']
train = train.drop(drop_elements, axis = 1)
train = train.drop(['categorical_age', 'categorical_fare'], axis = 1)
test = test.drop(drop_elements, axis = 1)

colormap = plt.cm.viridis  
plt.figure(figsize=(20,16))
plt.title('Pearson Correlation of Features', y=1.05, size=15)
sns.heatmap(train.astype(float).corr(), linewidths=0.5, vmax=1.0, square=True, cmap=colormap, linecolor='white', annot=True)

pplot = sns.pairplot(train[[u'Survived', u'Sex', u'Age', u'Parch', u'Fare', u'Embarked', u'family_size', u'Title']], hue='Survived', palette = 'seismic', size = 1.2, diag_kind = 'kde', diag_kws=dict(shade=True), plot_kws=dict(s=10))
pplot.set(xticklabels=[])

