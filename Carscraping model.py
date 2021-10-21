# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 09:53:40 2021


@author: jakob
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import time
import random

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier#, ExtraTreesRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import make_pipeline
# from sklearn.train_test_split import train_test_split 
from sklearn.model_selection import train_test_split

# %%
strBrandfile = r"D:\Carscarping\BrandModels.csv"
str_df_file = r"D:\Carscarping\Carscraping.xlsx"
str_df_file_copy = r"D:\Carscarping\Carscraping_copy.xlsx"

# get/set
def loadData():
    dfbrand_local = pd.read_csv(strBrandfile)
    # df = pd.read_excel(r"D:\Carscarping\BrandModels.xls")
    dfcarprice_local = pd.read_excel(str_df_file)
    dfcarprice_local.to_excel(str_df_file_copy)
    return dfbrand_local, dfcarprice_local

def saveData(dfbrand, dfcarprice):
    dfbrand.to_csv(strBrandfile, index=False)
    dfcarprice.to_excel(str_df_file_copy, index=False)



# todo trim dataset for models/brands with less than 5 cars.

# remove strings (brand model )
def init_prep_data():
    dfbrand = pd.DataFrame()
    dfcarprice = pd.DataFrame()
    dfbrand, dfcarprice = loadData()
    print('There are '+ str(len(dfcarprice)) + ' cars in the original dataset')

    # sets the ones with no data in km to zero NB. could be a mistake.
    dfcarprice['Km'] = dfcarprice['Km'].fillna(0)
    # removes the empty nan in hk 
    # nices the input, and saves it.
    dfcarprice = dfcarprice[dfcarprice['HK']. notna()]
    dfcarprice = dfcarprice[~dfcarprice.price.str.contains("ring")]
    dfcarprice = dfcarprice[~dfcarprice.price.str.contains("Ring")]
    dfcarprice['price'] = dfcarprice['price'].str.replace(' kr', '')
    dfcarprice['price'] = dfcarprice['price'].str.replace('.', '', regex=True)
    
    # km/l nan replaced with 100. and format changed to float
    dfcarprice['km_pr_l'] = dfcarprice['km_pr_l'].str.replace(',', '.', regex=True)
    dfcarprice['km_pr_l'] = dfcarprice['km_pr_l'].astype(float)
    dfcarprice['km_pr_l'] = dfcarprice['km_pr_l'].fillna(100)
    
    # price changed to float
    dfcarprice['price'] = dfcarprice['price'].astype(float)
    saveData(dfbrand, dfcarprice)

    print('There are '+ str(len(dfcarprice)) + ' cars in the dataset after trimming')
    return dfbrand, dfcarprice




#%%
def create_model():
    n_est = 1000
    dpt = 10
    mf = 200
    Model1, modelnavn = RandomForestRegressor(n_estimators=n_est, max_depth=dpt, max_features=mf,random_state=0), "RandomForestRegressor(n_estimators="+str(n_est)+", max_depth="+str(dpt)+", max_features="+str(mf)+",random_state=0)"
    return Model1

def giveX_Y(dfcarprice):
    X = dfcarprice[['Brand','Model','year','Km','HK','km_pr_l']]
    # dfcarprice.drop(['link'], axis =1)
    X = pd.get_dummies(data=X, drop_first=True)
    Y = dfcarprice['price']
    # train, test = train_test_split(dfcarprice, test_size=0.3, random_state=42, shuffle=True)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .20, random_state = 42, shuffle=True)
    return X, X_train, X_test, Y_train, Y_test


# Model1.fit(X_train, Y_train)


# forsaving = pd.DataFrame(dfcarprice)
# forsaving['guess'] = Model1.predict(X)
# forsaving['guess'] = forsaving['guess'].astype(int)
# forsaving['Diff'] = (forsaving['guess']-forsaving['price'])
# forsaving['payoff'] = (forsaving['guess']-forsaving['price'])/forsaving['price']

# # oprydning i datasettet. Der bør ikke være nogen rækker med en payoff på over 200% 

# cleanfornexttime_df = forsaving.loc[(forsaving['payoff']<2.0) & (forsaving['payoff']>-0.5)]

def createGuess(dfcarprice, X, Model1):
    
    guess_df = pd.DataFrame(dfcarprice)    
    guess_df['guess'] = Model1.predict(X)
    guess_df['guess'] = guess_df['guess'].astype(int)
    guess_df['Diff'] = (guess_df['guess']-guess_df['price'])
    guess_df['payoff'] = (guess_df['guess']-guess_df['price'])/guess_df['price']
    
    cleanfornexttime_df = guess_df.loc[(guess_df['payoff']<2.0) & (guess_df['payoff']>-0.5)]
    return guess_df, cleanfornexttime_df
# main()forsaving

def main():
    dfbrand, dfcarprice = init_prep_data()
    model = create_model()
    X, X_train, X_test, Y_train, Y_test = giveX_Y(dfcarprice)
    model.fit(X_train, Y_train)
    
    guess_df, cleanfornexttime_df = createGuess(dfcarprice, X, model)
    
    
    #we will stop the loop when we are within 5 to avoid it going on too long.
    while(5+len(cleanfornexttime_df)<len(guess_df)):
        print('There are '+ str(len(cleanfornexttime_df)) + ' cars in the dataset after trimming')
        X, X_train, X_test, Y_train, Y_test = giveX_Y(cleanfornexttime_df)
        model.fit(X_train, Y_train)
        guess_df, cleanfornexttime_df = createGuess(cleanfornexttime_df, X, model)
        guess_df.sort_values(by=['payoff'], inplace=True)
        print(guess_df.iloc[-1])
        print(guess_df.iloc[-1]['link'])
    print("saving")
    guess_df.to_excel(r"D:\Carscarping\firstguess.xlsx")
    
main()