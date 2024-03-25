import pandas as pd

class DataManager:
    def __init__(self, brand_file, df_file, subcategories_file):
        self.brand_file = brand_file
        self.df_file = df_file
        self.subcategories_file = subcategories_file
        self.df_brand = pd.DataFrame()
        self.df_car_price = pd.DataFrame()
        self.subcategories = []

    def load_data(self):
        self.df_brand = pd.read_csv(self.brand_file)
        try:
            self.df_car_price = pd.read_excel(self.df_file, engine='openpyxl')
        except ValueError as e:
            logger.error(f"Error: {e}")
            logger.error(f"DF not found: {self.df_file}")
        subcategories_df = pd.read_csv(self.subcategories_file)
        self.subcategories = subcategories_df['subcat'].tolist()

    def save_data(self):
