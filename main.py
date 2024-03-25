# main.py

import pandas as pd
import numpy as np
import re
import time
import random
import schedule
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from constants import BRAND_FILE, DF_FILE, SUBCATEGORIES_FILE

# Define file paths
strBrandfile = "BrandModels.csv"
str_df_file_temp = "Carscraping.xls"
str_df_file = "Carscraping.xlsx"
str_df_file_csv = "Carscraping.csv"
subcatagories_df_file = "subcats.csv"

# Define list of column names for dataframes
DFListNames = ['link', 'Brand', 'Model', 'year', 'Km', 'HK', 'km_pr_l', 'price',
               'FirstSeen', 'LastSeen', 'Description', 'Dealer']
# Initialize data manager
data_manager = DataManager(BRAND_FILE, DF_FILE, SUBCATEGORIES_FILE)

# Initialize global variables
dfbrand = pd.DataFrame()
dfcarprice = pd.DataFrame()
subcatagories = []

# Load data from files
def loadData():
    global dfbrand, dfcarprice, subcatagories
    dfbrand = pd.read_csv(strBrandfile)
    try:
        dfcarprice = pd.read_excel(str_df_file, engine='openpyxl')
    except ValueError as e:
        logger.error(f"Error: {e}")
        logger.error(f"DF not found: {str_df_file}")
    subcatagories_df = pd.read_csv(subcatagories_df_file)
    subcatagories = subcatagories_df['subcat'].tolist()

# Save data to files
def saveData():
    global dfbrand, dfcarprice, subcatagories
    logger.info("Converting the DF to utf ASCII")
    dfcarprice = dfcarprice.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
    logger.info("Saving dataframe")
    try:
        dfbrand.to_csv(strBrandfile, index=False)
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Unable to write to: {strBrandfile}")
    try:
        dfcarprice.to_excel(str_df_file, index=False, engine='openpyxl')
    except ValueError as e:
        logger.error(f"Error: {e}")
        logger.error(f"Unable to write to: {str_df_file}")
        logger.info('Saving it to CSV...')
        try:
            dfcarprice.to_csv(str_df_file_csv, index=False)
            logger.info('Saving it to CSV...DONE')
        except ValueError as e:
            logger.error(f"Error: {e}")
            logger.info('Saving it to CSV...FAILED')
    try:
        subcatagories_df = pd.DataFrame(subcatagories, columns=['subcat'])
        subcatagories_df.to_csv(subcatagories_df_file, index=False)
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.error(f"Unable to write to: {subcatagories_df_file}")

# Scrape data from website
def gothroughPages(url):
    global dfbrand, dfcarprice
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    try:
        dropdown = Select(driver.find_element(By.ID, 'itemsPerPage'))
        dropdown.select_by_value('96')
    except Exception as e:
        logger.error(f"Not able to set the 96: {e}")
    time.sleep(1)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    driver.close()
    dfbrand, dfcarprice = AddSoupToDF(soup, dfbrand, dfcarprice)

# Process BeautifulSoup object and update dataframes
def AddSoupToDF(soup, dfbrand, dfcarprice):
    # Your implementation of this function...
    return dfbrand, dfcarprice

# Main function to execute scraping
def main():
    global dfbrand, dfcarprice
    loadData()
    uniquebrands = dfbrand["Brand"].unique()
    for brand in uniquebrands:
        logger.info(f"Processing brand: {brand}")
        i = 1
        while True:
            url = f"https://www.bilbasen.dk/brugt/bil/{brand}?IncludeEngrosCVR=false&PriceFrom=0&includeLeasing=false&NewAndUsed=2&WithInLast=30&IncludeWithoutVehicleRegistrationTax=false&IncludeSellForCustomer=false&page={i}"
            logger.info(f"Processing page {i} for brand {brand}")
            gothroughPages(url)
            # Implement logic to break loop based on page contents or conditions
            # For example, check if there are no more listings for the brand
            # if <condition>:
            #     break
            i += 1
            # Add delay between requests if necessary
            time.sleep(random.uniform(1, 3))
    saveData()

# Schedule main function to run daily at 18:00
schedule.every().day.at("18:00").do(main)

# Run the main function immediately
main()

# Keep the script running to execute scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)