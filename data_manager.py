from loguru import logger
import pandas as pd
from constants import BRAND_FILE, DF_FILE, SUBCATEGORIES_FILE, DF_COLUMN_NAMES

class DataManager:
    def __init__(self):
        self.brand_file = BRAND_FILE
        self.df_file = DF_FILE
        self.subcategories_file = SUBCATEGORIES_FILE
        self.df_brand = pd.DataFrame()
        self.df_car_price = pd.DataFrame(columns=DF_COLUMN_NAMES)
        self.subcategories = []

    def load_data(self):
        self.df_brand = pd.read_csv(self.brand_file)

        try:
            self.df_car_price = pd.read_excel(self.df_file)
        except ValueError as e:
            logger.error(f"Error: {e}")
            logger.error(f"DF not found: {self.df_file}")
        except Exception as e:
            logger.error(f"unknown error found while reading excel file{self.df_file}: {e}")
        subcategories_df = pd.read_csv(self.subcategories_file)
        self.subcategories = subcategories_df['subcat'].tolist()

    def save_data(self):
        logger.info("Saving data...")
        try:
            self.df_brand.to_csv(self.brand_file, index=False)
            self.df_car_price.to_excel(self.df_file, index=False, columns=DF_COLUMN_NAMES)
            pd.DataFrame(self.subcategories, columns=['subcat']).to_csv(self.subcategories_file, index=False)
            logger.success("Data saved successfully.")
        except Exception as e:
            logger.exception(f"Error saving data: {e}")