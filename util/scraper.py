from loguru import logger
from data_manager import DataManager
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class Scraper:
    def __init__(self, data_manager: DataManager):
        self.dm = data_manager

    def go_through_page(self, url: str) -> (int, int):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.headless = True
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(1)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        driver.close()
        new_cars = self.add_soup_to_df(soup)
        return Scraper.find_last_page(soup), new_cars

    @staticmethod
    def find_last_page(soup: BeautifulSoup) -> int:
        if "pagination-total" in str(soup.find_all("span")):
            pos = str(soup.find_all("span")).index("pagination-total")
            return int(str(soup.find_all("span"))[pos + 18:pos + 22].split("<")[0])
        else:
            return 50

    def add_soup_to_df(self, soup: BeautifulSoup):
        new_cars = 0
        sf = soup.find_all("article", class_=["Listing_listing__XwaYe"])

        for soo in sf:
            car_http_link = soo.find("a", class_="Listing_link__6Z504")["href"]
            car_brand = car_http_link.split('/')[5]
            car_model = car_http_link.split('/')[6]

            if not (((self.dm.df_brand['Brand'] == car_brand) & (self.dm.df_brand['Model'] == car_model)).any()):
                self.dm.df_brand.loc[len(self.dm.df_brand.index)] = [car_brand, car_model]
            car_sub_categories = car_http_link.split('/')[7].split('-')
            self.dm.subcategories.extend([sub for sub in car_sub_categories if not sub in self.dm.subcategories])

            # front for KM and year
            listing_details = soo.find_all("div", class_="Listing_details__bkAK3")[0].find_all("li")
            year = listing_details[0].text
            km = listing_details[1].text
            km_pr_l = listing_details[2].text
            fuel_type = "El"
            gear_type = "automatisk gear"
            if len(listing_details) > 4:
                gear_type = listing_details[3].text
                fuel_type = listing_details[4].text
            price = soo.find("div", class_="Listing_price__6B3kE").text
            hk = float('NaN')

            # description
            description = ''
            if soo.find("div", class_=["Listing_description__sCNNM"]):
                description = soo.find("div", class_=["Listing_description__sCNNM"]).text

            # if we don't have the link in the "df": the car is unknown.
            if not ((self.dm.df_car_price['link'] == car_http_link).any()):
                self.dm.df_car_price.loc[len(self.dm.df_car_price.index)] = [car_http_link, car_brand, car_model, year,
                                                                             km, hk, km_pr_l, price, gear_type,
                                                                             fuel_type,
                                                                             car_sub_categories, pd.Timestamp.now(),
                                                                             pd.Timestamp.now(), str(description)]
                new_cars = new_cars + 1
            else:
                self.dm.df_car_price.loc[self.dm.df_car_price['link'] == car_http_link, 'LastSeen'] = pd.Timestamp.now()
        logger.info(f"{new_cars} new cars found on the site")
        return new_cars
