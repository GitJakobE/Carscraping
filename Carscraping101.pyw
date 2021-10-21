# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 14:30:34 2021

@author: jakob
"""

from urllib.request import urlopen

import requests
import pandas as pd
import numpy as np
import re
import time
import random
import schedule
from bs4 import BeautifulSoup

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier#, ExtraTreesRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.pipeline import make_pipeline
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


s=Service(ChromeDriverManager().install())
# %%
DFListNames = ['link','Brand', 'Model', 'year', 'Km', 'HK','km_pr_l','price','FirstSeen','LastSeen', 'Description', 'Dealer']
dfbrand = pd.DataFrame()
dfcarprice = pd.DataFrame()
strBrandfile = r"D:\Carscarping\BrandModels.csv"
str_df_file_temp = r"D:\Carscarping\Carscraping.xls"
str_df_file = r"D:\Carscarping\Carscraping.xlsx"


# get/set
def loadData():
    dfbrand_local = pd.read_csv(strBrandfile)
    # df = pd.read_excel(r"D:\Carscarping\BrandModels.xls")
    dfcarprice_local = pd.DataFrame(columns=DFListNames)
    try:
        dfcarprice_local = pd.read_excel(str_df_file)
    except:
        print('DF not found: '+ str_df_file)
        
    return dfbrand_local, dfcarprice_local

def saveData(dfbrand, dfcarprice):
    dfbrand.to_csv(strBrandfile, index=False)
    dfcarprice.to_excel(str_df_file, index=False)

#%%
def gothroughPages(url, dfbrand, dfcarprice, hds):
        # localurl = url +"&page="+str(pagenr)
     # user_agent = get_random_ua()
     # headers = {'user-agent': user_agent}

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    # chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    # driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
    chrome_options.headless = True
    # driver = webdriver.Chrome('C:\windows\chromedriver.exe', options=chrome_options)
    
    driver = webdriver.Chrome(service=s, options=chrome_options)
    #get the website
    driver.get(url)#'https://yourwebsite.com')
    try:
        
        # Get the element by ID
        dropdown= Select(driver.find_element(By.ID,'itemsPerPage'))
        
        #Click on the dropdown
        dropdown.select_by_value('96')
    except:
        print("NOt Able to set the 96*******************************")
    
    time.sleep(1)
    page = driver.page_source 
    # page = requests.get(url,headers=hds)
    # print('Processing..' + url)
    # driver = webdriver.PhantomJS(service_args=service_args)
    # print(url)
    # print(page.text)
    soup = BeautifulSoup(page, "html.parser")
    # page.close()
    driver.close()
    dfbrand, dfcarprice = AddSoupTooDF(soup, dfbrand, dfcarprice)
    print("carprices :" + str(len(dfcarprice)) + "   models: "+ str(len(dfbrand)))
    
    localAntalbiler = 32
    titel =(re.findall(r'\d+',soup.find("title").text))
    if(len(titel)>0):
        localAntalbiler = (int) (titel[0])
    print("Der er {} biler i mærket".format(localAntalbiler))
    return localAntalbiler, dfbrand, dfcarprice
   
def AddSoupTooDF(soup, dfbrand, dfcarprice):
    
    newcars =0
    sf = soup.find_all("div", class_=["row listing listing-discount bb-listing-clickable", "row listing listing-plus bb-listing-clickable", "row listing listing-exclusive bb-listing-clickable"])
    
    
    print(str(len(sf)) + " biler fundet på siden")
    for soo in sf:
        
        
        # print(type(soo))
        ss = soo.find("a", class_="listing-heading darkLink")
        carlink = "www.bilbasen.dk"+ss["href"]
        # print(ss.text)
        
        sslist = (ss.text).split(" ")
        Brand = sslist[0]
        Model = sslist[1]
        
        
        if(not(((dfbrand['Brand'] == Brand) & (dfbrand['Model'] == Model)).any()) ):
            df2 = pd.DataFrame([[Brand, Model]], columns=['Brand', 'Model'])
            
            dfbrand  = dfbrand.append(df2, ignore_index=True)
        
        
        # front for KM and year
        yearkm = soo.find_all("div", class_ = "col-xs-2 listing-data");
        
        # KM
        kmlist = re.findall(r'\d+.\d+',yearkm[1].text)
        km = float('NaN')
        if(len(kmlist)>0):
            km = kmlist[0]
        
        # Year
        year = yearkm[2].text
        pris = soo.find("div", class_ = "col-xs-3 listing-price").text
        hklist = re.findall(r'\d+',soo.find("span", class_ = "variableDataColumn")["data-hk"])
        hk = float('NaN')
        if(len(hklist)>0):
            hk = hklist[0]
         
        # km/L
        # print(hk)
        km_pr_l_list = re.findall(r'\d+.\d+',soo.find("div", class_ = "col-xs-3 listing-data").text)
        km_pr_l = float('NaN')
        if(len(km_pr_l_list)>0):
            km_pr_l = km_pr_l_list[0]
        
        #description
        description = ''
        if(soo.find("div", class_=["listing-description expandable-box", "listing-description"])):
            description = soo.find("div", class_=["listing-description expandable-box", "listing-description"]).text
            # print(type(description))
            
        
        # private or forhandler
        b_forhandler = False
        if(soo.find("img", class_ = 'listing-dealer-logo-sm')):
             b_forhandler = True
        else:
            if(soo.find("span", class_ = 'dealer-private-string')):
                if('Forhandler' in soo.text or 'forhandler' in soo.text):
                    b_forhandler =True
        
        # print(km_pr_l)
        # if we don't have the link in the "df": the car is unknown.
        if(not((dfcarprice['link'] == carlink).any())):
            dfcarprice2 = pd.DataFrame([[carlink, Brand, Model, year, km, hk, km_pr_l, pris, pd.Timestamp.now(),pd.Timestamp.now(), str(description), b_forhandler]], columns=DFListNames)
            # print(dfcarprice2)
            dfcarprice = dfcarprice.append(dfcarprice2)
            newcars = newcars+1
            # print(Brand +"\t"+ Model+"\t"+year)
        else:
            dfcarprice.loc[dfcarprice['link'] == carlink, 'LastSeen'] = pd.Timestamp.now()
            dfcarprice.loc[dfcarprice['link'] == carlink, 'Description'] = str(description)
            dfcarprice.loc[dfcarprice['link'] == carlink, 'Dealer'] = b_forhandler
        #     print(Brand +"\t"+ Model+"\t"+year)
        # "col-xs-3 listing-price"
    # 
    return dfbrand, dfcarprice
    
# %%
def main():
    
    n =0

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
    dfbrand, dfcarprice = loadData()
    rate = [1,2]
    print(dfbrand)
    uniquebrands = dfbrand["Brand"].unique()
    # uniquebrands = ['Peugeot']
    
    antalbiler = 100
    antalsider = (int)(antalbiler/96) +1
    
    for brand in uniquebrands:
        n = n+1
        print(str(n) + " brand of "+ str(len(uniquebrands))+ ": "+brand)
        # urllist = ["https://www.bilbasen.dk/brugt/bil?includeengroscvr=true&pricefrom=0&includeleasing=false&page="+str(i) for i in range(98, 1000)]
        # urllist = ["https://www.bilbasen.dk/brugt/bil/"+brand+"?includeengroscvr=true&pricefrom=0&includeleasing=false&page="+str(i) for i in range(1, antalsider)]
        i =1
        antalsider=100
        dfbrand, dfcarprice = loadData()
        while(i<antalsider+1):
            
            url = "https://www.bilbasen.dk/brugt/bil/"+brand+"?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast=30&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false&page="+str(i)
                  # "https://www.bilbasen.dk/brugt/bil/peugeot?includeengroscvr=false&pricefrom=0&includeleasing=false&newandused=2&withinlast=2&includewithoutvehicleregistrationtax=false&includesellforcustomer=false&page=2"
            #     "https://www.bilbasen.dk/brugt/bil/"+brand+"?includeengroscvr=true&pricefrom=0&includeleasing=false&page="+str(i)
                # url =https://www.bilbasen.dk/brugt/bil/Peugeot?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast=2&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false
                  # "https://www.bilbasen.dk/brugt/bil/Peugeot?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast=2&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false"
                  # "https://www.bilbasen.dk/brugt/bil/Peugeot?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast=2&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false"
            
            
            #On the page it says how many cars there are in the brand. That determines how many pages we will go through
            antalbiler, dfbrand, dfcarprice = gothroughPages(url, dfbrand, dfcarprice, headers)
            # print(type(antalbiler))
            antalsider = (int)(antalbiler/96) +1
            
            print(brand + ": side " + str(i) +" af " +str(antalsider))
            # time.sleep(random.choice(rate))
            i= i+1
        saveData(dfbrand, dfcarprice)
    print('Main finishing')

# %%
# schedule.every(1).second.do(mainTEST)
# schedule.every().hour.do(main2)
schedule.every().day.at("18:00").do(main)
print('Starting carscraping101')
while 1:
    schedule.run_pending()
    time.sleep(1)

    
