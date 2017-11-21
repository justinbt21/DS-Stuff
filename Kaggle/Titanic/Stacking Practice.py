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
# import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt
import os
import plotly.offline as py
import plotly.graph_objs as go
import plotly.tools as tls
import warnings
# Going to use these 5 base models for the stacking
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier,\
    GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.cross_validation import KFold
from IPython import get_ipython
# get_ipython().run_line_magic('matplotlib', 'inline')
py.init_notebook_mode(connected=True)
warnings.filterwarnings('ignore')
os.chdir('C:/Users/justintran/Documents/GitHub/Kaggle')
# os.chdir('/Users/justinbt/Documents/GitHub/Kaggle/')

# Load in the train and test datasets
train = pd.read_csv('Titanic/Data/train.csv')
test = pd.read_csv('Titanic/Data/test.csv')

PassengerId = test['PassengerId']
full_data = [train, test]

# Engineered Features

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
train['categorical_fare'] = pd.qcut(train['Fare'], 4, labels=[0, 1, 2, 3])

# Categorical Age
for dataset in full_data:
    age_avg = dataset['Age'].mean()
    age_std = dataset['Age'].std()
    age_null_count = dataset['Age'].isnull().sum()
    age_null_random_list = np.random.randint(age_avg - age_std, age_avg + age_std,
                                             size=age_null_count)
    dataset['Age'][np.isnan(dataset['Age'])] = age_null_random_list
train['categorical_age'] = pd.cut(train['Age'], 5, labels=[0, 1, 2, 3, 4])

# Title


def get_title(name):
    title_search = re.search(' ([A-Za-z]+)\.', name)
    # If the title exists, extract and return it.
    if title_search:
        return title_search.group(1)
    return ""


for dataset in full_data:
    dataset['Title'] = dataset['Name'].apply(get_title)

# Group all non-common titles into on single grouping "Rare"
for dataset in full_data:
    dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess', 'Capt', 'Col', 'Don', 'Dr',
                                                'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
    dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')


for dataset in full_data:
    # Mapping Sex
    dataset['Sex'] = dataset['Sex'].map({'female': 0, 'male': 1}).astype(int)
    # Mapping titles
    title_mapping = {'Mr': 1, 'Miss': 2, 'Mrs': 3, 'Master': 4, 'Rare': 5}
    dataset['Title'] = dataset['Title'].map(title_mapping)
    dataset['Title'] = dataset['Title'].fillna(0)
    # Mapping Embarked
    dataset['Embarked'] = dataset['Embarked'].map({'S': 0, 'C': 1, 'Q': 2}).astype(int)
    # Mapping Fare
    dataset.loc[dataset['Fare'] <= 7.91, 'Fare'] = 0
    dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
    dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare'] = 2
    dataset.loc[(dataset['Fare'] > 31), 'Fare'] = 3
    dataset['Fare'] = dataset['Fare'].astype(int)
    # Mapping Age
    dataset.loc[dataset['Age'] <= 16, 'Age'] = 0
    dataset.loc[(dataset['Age'] > 16) & (dataset['Age'] <= 32), 'Age'] = 1
    dataset.loc[(dataset['Age'] > 32) & (dataset['Age'] <= 48), 'Age'] = 2
    dataset.loc[(dataset['Age'] > 48) & (dataset['Age'] <= 64), 'Age'] = 3
    dataset.loc[dataset['Age'] > 64, 'Age'] = 4
# Feature selection
drop_elements = ['PassengerId', 'Name', 'Ticket', 'Cabin', 'SibSp']
train = train.drop(drop_elements, axis=1)
train = train.drop(['categorical_age', 'categorical_fare'], axis=1)
test = test.drop(drop_elements, axis=1)

colormap = plt.cm.viridis
plt.figure(figsize=(20, 16))
plt.title('Pearson Correlation of Features', y=1.05, size=15)
sns.heatmap(train.astype(float).corr(), linewidths=0.5, vmax=1.0, square=True, cmap=colormap,
            linecolor='white', annot=True)

pplot = sns.pairplot(train[[u'Survived', u'Sex', u'Age', u'Parch', u'Fare', u'Embarked',
                     u'family_size', u'Title']], hue='Survived', palette='seismic', size=1.2,
                     diag_kind='kde', diag_kws=dict(shade=True), plot_kws=dict(s=10))
pplot.set(xticklabels=[])

# Some useful parameters which will come in handy later on
ntrain = train.shape[0]
ntest = test.shape[0]
# for reproducibility
SEED = 0
# set folds for out of fold prediction
NFOLDS = 5
kf = KFold(ntrain, n_folds=NFOLDS, random_state=SEED)

# Class to extend the Sklearn classifier


class SklearnHelper(object):
    def __init__(self, clf, seed=0, params=None):
        params['random_state'] = seed
        self.clf = clf(**params)

    def train(self, x_train, y_train):
        self.clf.fit(x_train, y_train)

    def predict(self, x):
        return self.clf.predict(x)

    def fit(self, x, y):
        return self.clf.fit(x, y)

    def feature_importances(self, x, y):
        print(self.clf.fit(x, y).feature_importances_)

# Class to extend XGboost classifier


def get_oof(clf, x_train, y_train, x_test):
    oof_train = np.zeros((ntrain,))
    oof_test = np.zeros((ntest,))
    oof_test_skf = np.empty((NFOLDS, ntest))

    for i, (train_index, test_index) in enumerate(kf):
        x_tr = x_train[train_index]
        y_tr = y_train[train_index]
        x_te = x_train[test_index]

        clf.train(x_tr, y_tr)

        oof_train[test_index] = clf.predict(x_te)
        oof_test_skf[i, :] = clf.predict(x_test)

    oof_test[:] = oof_test_skf.mean(axis=0)
    return oof_train.reshape(-1, 1), oof_test.reshape(-1, 1)


# Put in our parameters for said classifiers
# Random Forest parameters
rf_params = {
    'n_jobs': -1,
    'n_estimators': 500,
    'warm_start': True,
    #'max_features': .2
    'max_depth': 6,
    'min_samples_leaf': 2,
    'max_features' : 'sqrt',
    'verbose' : 0
}

# Extra Tree Parameters
et_params = {
    'n_jobs': -1,
    'n_estimators': 500,
    #'max_features': .5
    'max_depth': 8,
    'min_samples_leaf': 2,
    'verbose' : 0
}

# AdaBoost parameters
ada_params = {
    'n_estimators': 500,
    'learning_rate': .75
}

# Gradient Boosting parameters
gb_params = {
   'n_estimators': 500,
    #'max_features': .2
    'max_depth': 5,
    'min_samples_leaf': 2,
    'verbose' : 0
}

# Support Vector Classifier parameters
svc_params = {
    'kernel' : 'linear',
    'C' : 0.025
}

# Create 5 objects that represent our 4 models
rf = SklearnHelper(clf=RandomForestClassifier, seed=SEED, params=rf_params)
et = SklearnHelper(clf=ExtraTreesClassifier, seed=SEED, params=et_params)
ada = SklearnHelper(clf=AdaBoostClassifier, seed=SEED, params=ada_params)
gb = SklearnHelper(clf=GradientBoostingClassifier, seed=SEED, params=gb_params)
svc = SklearnHelper(clf=SVC, seed=SEED, params=svc_params)

# Create Numpy arrays of train, test and target (Survived) dataframs to feed into our models
y_train = train['Survived'].ravel()
train = train.drop(['Survived'], axis=1)
# Creates an array of the train data
x_train = train.values
# Creates an array of the test data
x_test = test.values

# Create our OOF train and test predictions. These base results will be used as new features
# Extra Trees
et_oof_train, et_oof_test = get_oof(et, x_train, y_train, x_test)
# Random Forest
rf_oof_train, rf_oof_test = get_oof(rf, x_train, y_train, x_test)
# AdaBoost
ada_oof_train, ada_oof_test = get_oof(ada, x_train, y_train, x_test)
# Gradient Boost
gb_oof_train, gb_oof_test = get_oof(gb, x_train, y_train, x_test)

print('Training is complete')

rf_feature = rf.feature_importances(x_train, y_train)
et_feature = et.feature_importances(x_train, y_train)
ada_feature = ada.feature_importances(x_train, y_train)
gb_feature = gb.feature_importances(x_train, y_train)
