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
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

# %%
DFListNames = ['link','Brand', 'Model', 'year', 'Km', 'HK','km_pr_l','price','FirstSeen','LastSeen', 'Description', 'Dealer']
strBrandfile = r"D:\Carscarping\BrandModels.csv"
str_df_file = r"D:\Carscarping\Carscraping - backup.xlsx"
str_df_file_copy = r"D:\Carscarping\Carscraping_copy.xlsx"
subcatagories_df_file =  r"D:\Carscarping\subcats.csv"
subcatagories = [] 

# get/set
def loadData():
    print('loading DF')
    dfbrand_local = pd.read_csv(strBrandfile)
    # df = pd.read_excel(r"D:\Carscarping\BrandModels.xls")
    dfcarprice_local = pd.DataFrame()
    subcatagories_df = pd.read_csv(subcatagories_df_file)
    subcatagories = subcatagories_df['subcat'].tolist()
    try:
        dfcarprice_local = pd.read_excel(str_df_file)
    except:
        print('DF not found: '+ str_df_file)
    print('DF loaded')
    return dfbrand_local, dfcarprice_local, subcatagories

    #dfbrand_local = pd.read_csv(strBrandfile)
    # df = pd.read_excel(r"D:\Carscarping\BrandModels.xls")
    #dfcarprice_local = pd.read_excel(str_df_file)
    #dfcarprice_local.to_excel(str_df_file_copy)
    #return dfbrand_local, dfcarprice_local

def saveData(dfbrand, dfcarprice):
    dfbrand.to_csv(strBrandfile, index=False)
    dfcarprice.to_excel(str_df_file_copy, index=False)


# %%
# todo trim dataset for models/brands with less than 5 cars.

# remove strings (brand model )
def init_prep_data():
    dfbrand = pd.DataFrame()
    dfcarprice = pd.DataFrame()
    dfbrand, dfcarprice, subcatagories = loadData()
    print('There are '+ str(len(dfcarprice)) + ' cars in the original dataset')
    # sets the ones with no data in km to zero NB. could be a mistake.
    dfcarprice['Km'] = dfcarprice['Km'].fillna(0)
    # removes the empty nan in hk 
    # nices the input, and saves it.
    dfcarprice = dfcarprice[dfcarprice['HK']. notna()]
    dfcarprice = dfcarprice[~dfcarprice.price.astype(str).str.contains("ring")]
    dfcarprice = dfcarprice[~dfcarprice.price.astype(str).str.contains("Ring")]
    dfcarprice['price'] = dfcarprice['price'].astype(str).str.replace(' kr', '') 
    dfcarprice['price'] = dfcarprice['price'].astype(str).str.replace('.', '', regex=True)
    dfcarprice['price'] = dfcarprice['price'].astype(float)
    # km/l nan replaced with 100. and format changed to float
    dfcarprice['km_pr_l'] = dfcarprice['km_pr_l'].str.replace(',', '.', regex=True)
    dfcarprice['km_pr_l'] = dfcarprice['km_pr_l'].astype(float)
    dfcarprice['km_pr_l'] = dfcarprice['km_pr_l'].fillna(100)
    saveData(dfbrand, dfcarprice)
    print('There are '+ str(len(dfcarprice)) + ' cars in the dataset after trimming')
    #finding the number of doors
    dfcarprice['doors'] = [lastelement[-1] for lastelement in (dfcarprice['link'].astype(str).str.split("/", expand =True))[5].str.split("-").values]
    dfcarprice['cubic'] = [lastelement[0] for lastelement in (dfcarprice['link'].astype(str).str.split("/", expand =True))[5].str.split("-").values]
    word = 'TDI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'TSI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'TfSI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = '-gt-'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'VAN'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'HDI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'aut'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'GTE'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'GTI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'DCI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'CDI'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'PHEV'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    word = 'hybrid'
    dfcarprice.loc[dfcarprice['link'].str.contains(word, case=False), word] =1
    dfcarprice.loc[~(dfcarprice['link'].str.contains(word, case=False)), word] =0
    print('Added features to DF')
    return dfbrand, dfcarprice


#%%
def create_models():
    n_est = 1000
    dpt = 10
    mf = 200
    ModelRF, modelnavn = RandomForestRegressor(n_estimators=n_est, max_depth=dpt, max_features=mf,random_state=0), "RandomForestRegressor(n_estimators="+str(n_est)+", max_depth="+str(dpt)+", max_features="+str(mf)+",random_state=0)"
    neighboors = 3
    ModelNN = NearestNeighbors(n_neighbors=2, algorithm='ball_tree')
    return ModelRF, ModelNN

def giveX_Y(dfcarprice):
    X = dfcarprice[['Brand','Model','year','Km','HK','km_pr_l', 'doors', 'cubic', 'TDI','TSI','TfSI','-gt-','VAN','HDI','aut','GTE','GTI','DCI','CDI','PHEV','hybrid']]
    # dfcarprice.drop(['link'], axis =1)
    X = pd.get_dummies(data=X, drop_first=True)
    Y = dfcarprice['price']
    # train, test = train_test_split(dfcarprice, test_size=0.3, random_state=42, shuffle=True)
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = .20, random_state = 42, shuffle=True)
    return X, X_train, X_test, Y_train, Y_test


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
    modelRF, modelNN = create_models()
    X, X_train, X_test, Y_train, Y_test = giveX_Y(dfcarprice)
    modelRF.fit(X_train, Y_train)
    modelNN.fit(X_train, Y_train)

    guess_df, cleanfornexttime_df = createGuess(dfcarprice, X, modelRF)
    
    
    #we will stop the loop when we are within 5 to avoid it going on too long.
    while(5+len(cleanfornexttime_df)<len(guess_df)):
        print('There are '+ str(len(cleanfornexttime_df)) + ' cars in the dataset after trimming')
        X, X_train, X_test, Y_train, Y_test = giveX_Y(cleanfornexttime_df)
        print("fitting model...")
        modelRF.fit(X_train, Y_train)
        print("model fitted")
        guess_df, cleanfornexttime_df = createGuess(cleanfornexttime_df, X, modelRF)
        guess_df.sort_values(by=['payoff'], inplace=True)
        print(guess_df.iloc[-1])
        print(guess_df.iloc[-1]['link'])
    print("saving")
    guess_df.to_excel(r"D:\Carscarping\firstguess.xlsx")
    #From here on out we will add a number of features to filter on:
    fromyear = 2014
    notfrombrands =['audi', 'BMW', 'tesla']
    fromdealer = 0
    for excludedbrands in notfrombrands:
        guess_df = guess_df.loc[~(guess_df['Brand'] == excludedbrands)] 
    guess_df = guess_df.loc[~(guess_df['Dealer'] == fromdealer)]
    guess_df = guess_df.loc[guess_df['year'] > fromyear]
    guess_df.to_excel(r"D:\Carscarping\exclusiveguess.xlsx")

    
main()