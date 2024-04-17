from loguru import logger
import pandas as pd
from data_manager import DataManager

from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split


class DataModel:
    def init_prep_data(self, dm: DataManager) -> None:
        logger.info(f'There are {str(len(dm.df_car_price))} cars in the original dataset')
        # sets the ones with no data in km to zero NB. could be a mistake.
        dm.df_car_price['Km'] = dm.df_car_price['Km'].fillna(0)
        # removes the empty nan in hk
        # nices the input, and saves it.
        prices_to_remove = "Engros", "CVR", "ring", "Ring", "(Uden afgift)"
        for rem in prices_to_remove:
            dm.df_car_price = dm.df_car_price[~dm.df_car_price.price.astype(str).str.contains(rem)]
        dm.df_car_price['price'] = dm.df_car_price['price'].astype(str).str.replace(' kr', '')
        dm.df_car_price['price'] = dm.df_car_price['price'].astype(str).str.replace('.', '', regex=True)
        dm.df_car_price['price'] = dm.df_car_price['price'].astype(float)
        # km/l nan replaced with 100. and format changed to float
        dm.df_car_price['km_pr_l'] = dm.df_car_price['km_pr_l'].str.replace(',', '.', regex=True)
        dm.df_car_price['km_pr_l'] = dm.df_car_price['km_pr_l'].astype(float)
        dm.df_car_price['km_pr_l'] = dm.df_car_price['km_pr_l'].fillna(100)
        dm.save_data("_Model")
        logger.info(f'There are {str(len(dm.df_car_price))} cars in the dataset after trimming')
        # finding the number of doors
        dm.df_car_price['doors'] = [lastelement[-1] for lastelement in
                                    (dm.df_car_price['link'].astype(str).str.split("/", expand=True))[5].str.split(
                                        "-").values]
        dm.df_car_price['cubic'] = [lastelement[0] for lastelement in
                                    (dm.df_car_price['link'].astype(str).str.split("/", expand=True))[5].str.split(
                                        "-").values]
        parameter_words = ['TDI', 'TSI', 'TfSI', '-gt-', 'VAN', 'HDI', 'aut', 'GTE', 'GTI', 'DCI', 'CDI', 'PHEV',
                           'hybrid']
        for word in parameter_words:
            dm.df_car_price.loc[dm.df_car_price['link'].str.contains(word, case=False), word] = 1
            dm.df_car_price.loc[~(dm.df_car_price['link'].str.contains(word, case=False)), word] = 0
        logger.info('Added features to DF')

    def create_models(self):
        n_est = 1000
        dpt = 10
        mf = 200
        neighboors = 3
        ModelRF, modelnavn = (RandomForestRegressor(n_estimators=n_est, max_depth=dpt, max_features=mf, random_state=0),
                              f"RandomForestRegressor(n_estimators={n_est} max_depth= {dpt}, max_features={mf}, random_state={0}")

        ModelNN = NearestNeighbors(n_neighbors=neighboors, algorithm='ball_tree')
        return ModelRF, ModelNN

    def giveX_Y(self, dm: DataManager):
        X = dm.df_car_price[
            ['Brand', 'Model', 'year', 'Km', 'km_pr_l', 'doors', 'cubic', 'TDI', 'TSI', 'TfSI', '-gt-', 'VAN',
             'HDI', 'aut', 'GTE', 'GTI', 'DCI', 'CDI', 'PHEV', 'hybrid']]
        # dm.df_car_price.drop(['link'], axis =1)
        X = pd.get_dummies(data=X, drop_first=True)
        Y = dm.df_car_price['price']
        # train, test = train_test_split(dm.df_car_price, test_size=0.3, random_state=42, shuffle=True)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=.20, random_state=42, shuffle=True)
        return X, X_train, X_test, Y_train, Y_test

    def create_guess(self, dm, X, model):
        guess_df = pd.DataFrame(dm.df_car_price)
        guess_df['guess'] = model.predict(X)
        guess_df['guess'] = guess_df['guess'].astype(int)
        guess_df['Diff'] = (guess_df['guess'] - guess_df['price'])
        guess_df['payoff'] = (guess_df['guess'] - guess_df['price']) / guess_df['price']

        clean_for_next_time_df = guess_df.loc[(guess_df['payoff'] < 2.0) & (guess_df['payoff'] > -0.5)]
        return guess_df, clean_for_next_time_df

    def run_model(self):
        dm = DataManager()
        dm.load_data()
        self.init_prep_data(dm)
        model_rf, model_nn = self.create_models()
        X, X_train, X_test, Y_train, Y_test = self.giveX_Y(dm.df_car_price)
        model_rf.fit(X_train, Y_train)
        model_nn.fit(X_train, Y_train)

        guess_df, clean_for_next_time_df = self.create_guess(dm.df_car_price, X, model_rf)

        # we will stop the loop when we are within 5 to avoid it going on too long.
        while (5 + len(clean_for_next_time_df) < len(guess_df)):
            logger.info(f'There are {len(clean_for_next_time_df)} cars in the dataset after trimming')
            X, X_train, X_test, Y_train, Y_test = self.giveX_Y(clean_for_next_time_df)
            logger.info("fitting model...")
            model_rf.fit(X_train, Y_train)
            logger.info("model fitted")
            guess_df, clean_for_next_time_df = self.create_guess(clean_for_next_time_df, X, model_rf)
            guess_df.sort_values(by=['payoff'], inplace=True)
            logger.info(guess_df.iloc[-1])
            logger.info(guess_df.iloc[-1]['link'])
        logger.info("saving")
        guess_df.to_excel(r".\firstguess.xlsx")

        # From here on out we will add a number of features to filter on:
        from_year = 2014
        not_from_brands = ['audi', 'BMW', 'tesla']
        for excluded_brands in not_from_brands:
            guess_df = guess_df.loc[~(guess_df['Brand'] == excluded_brands)]
        guess_df = guess_df.loc[guess_df['year'] > from_year]
        guess_df.to_excel(r".\exclusive_guess.xlsx")
