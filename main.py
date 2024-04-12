import time
import random
import schedule

from loguru import logger
from data_manager import DataManager
from util import Scraper, Util

def main():
    logger.info("main running")
    data_manager = DataManager()
    data_manager.load_data()
    scraper = Scraper(data_manager)
    unique_brands = data_manager.df_brand["Brand"].unique()
    random.shuffle(unique_brands)  # so we don't debug on the same page every time
    days_back = 2
    total_new_cars = 0
    for n, brand in enumerate(unique_brands):
        logger.info(f"Processing {brand}. Brand #{n} of {len(unique_brands)}")
        i = 1
        while True:
            logger.info(f"Processing page {i} for brand: {brand}")
            try:
                total_pages_in_brand, new_cars = scraper.go_through_page(Util.generate_urls(brand, i, days_back))
                total_new_cars += new_cars
                logger.info(f"Finished processing page {i}/{total_pages_in_brand} for brand: {brand}")
            except Exception as e:
                logger.error(f"Something went wrong while processing page {i} of {brand}: {e}")
                break
            if total_new_cars > 100:
                data_manager.save_data()
                total_new_cars=0
            if i == total_pages_in_brand or total_pages_in_brand>days_back*5:
                break
            i += 1
            time.sleep(random.uniform(1, 3))
    logger.info("Finished scraping")

# run the script now and scedule it for 6 pm every day. Keep it running.
schedule.every().day.at("18:00").do(main)
logger.info("scheduler set")
main()
while True:
    schedule.run_pending()
    time.sleep(1)
