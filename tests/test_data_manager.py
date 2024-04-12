import os
import pandas as pd
import pytest
from data_manager import DataManager


@pytest.fixture
def setup_data_manager(tmpdir):
    # Set up test file paths
    brand_file_path = os.path.join(tmpdir, "test_BrandModels.csv")
    df_file_path = os.path.join(tmpdir, "test_Carscraping.xlsx")
    subcategories_file_path = os.path.join(tmpdir, "test_subcats.csv")

    # Create test files in the temporary directory
    with open(brand_file_path, 'w'):
        pass
    with open(df_file_path, 'w'):
        pass
    with open(subcategories_file_path, 'w'):
        pass

    # Initialize DataManager with test file paths
    data_manager = DataManager()
    data_manager.brand_file = brand_file_path
    data_manager.df_file = df_file_path
    data_manager.subcategories_file = subcategories_file_path

    # Set up test data
    data_manager.df_brand = pd.DataFrame({"Brand": ["Toyota", "Honda"], "Model": ["Camry", "Accord"]})
    data_manager.df_car_price = pd.DataFrame({"link": ["www.example.com/car1", "www.example.com/car2"],
                                              "Brand": ["Toyota", "Honda"],
                                              "Model": ["Camry", "Accord"]})
    data_manager.subcategories = ["SUV", "Sedan"]

    # Yield the initialized DataManager object
    yield data_manager

def test_load_data(setup_data_manager):
    # Load test data
    setup_data_manager.load_data()

    # Check if data is loaded correctly
    assert not setup_data_manager.df_brand.empty
    assert not setup_data_manager.df_car_price.empty
    assert setup_data_manager.subcategories == ["SUV", "Sedan"]


def test_save_data(setup_data_manager, tmpdir):
    # Save test data
    setup_data_manager.save_data()

    # Check if data is saved correctly
    brand_file = os.path.join(tmpdir, "test_BrandModels.csv")
    df_file = os.path.join(tmpdir, "test_Carscraping.xlsx")
    subcategories_file = os.path.join(tmpdir, "test_subcats.csv")

    assert os.path.isfile(brand_file)
    assert os.path.isfile(df_file)
    assert os.path.isfile(subcategories_file)

    # Check if saved data matches test data
    df_brand_saved = pd.read_csv(brand_file)
    df_car_price_saved = pd.read_excel(df_file)
    subcategories_saved = pd.read_csv(subcategories_file)["subcat"].tolist()

    assert df_brand_saved.equals(setup_data_manager.df_brand)
    assert df_car_price_saved.equals(setup_data_manager.df_car_price)
    assert subcategories_saved == setup_data_manager.subcategories