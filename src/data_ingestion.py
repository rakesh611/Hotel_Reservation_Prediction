import os
import pandas as pd
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)


class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]

        # ✅ Train-test split ratio
        self.train_test_ratio = self.config["train_ratio"]

        # ✅ LOCAL FILE PATH (your given path)
        self.source_file_path = "/home/aayush/Hotel_Reservation_Prediction/Hotel_Reservation_Prediction/artifacts/raw/Hotel Reservations.csv"

        # Create directories if not exist
        os.makedirs(RAW_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(TRAIN_FILE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(TEST_FILE_PATH), exist_ok=True)

        logger.info(f"Data Ingestion started using local file: {self.source_file_path}")

    def load_local_csv(self):
        try:
            # ✅ Read local CSV
            data = pd.read_csv(self.source_file_path)

            # Save raw copy (optional but good practice)
            data.to_csv(RAW_FILE_PATH, index=False)

            logger.info(f"CSV file loaded successfully from {self.source_file_path}")
            logger.info(f"Raw data saved to {RAW_FILE_PATH}")

            return data

        except Exception as e:
            logger.error("Error while loading local CSV file")
            raise CustomException("Failed to load local CSV file", e)

    def split_data(self, data):
        try:
            logger.info("Starting the splitting process")

            train_data, test_data = train_test_split(
                data,
                test_size=1 - self.train_test_ratio,
                random_state=42
            )

            # Save split data
            train_data.to_csv(TRAIN_FILE_PATH, index=False)
            test_data.to_csv(TEST_FILE_PATH, index=False)

            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")

        except Exception as e:
            logger.error("Error while splitting data")
            raise CustomException("Failed to split data into training and test sets", e)

    def run(self):
        try:
            logger.info("Starting data ingestion process")

            # ✅ Load from local instead of GCP
            data = self.load_local_csv()

            # ✅ Split data
            self.split_data(data)

            logger.info("Data ingestion completed successfully")

        except CustomException as ce:
            logger.error(f"CustomException: {str(ce)}")
            raise ce

        except Exception as e:
            logger.error("Unexpected error in data ingestion")
            raise CustomException("Unexpected error in data ingestion", e)

        finally:
            logger.info("Data ingestion pipeline finished")


if __name__ == "__main__":
    config = read_yaml(CONFIG_PATH)
    data_ingestion = DataIngestion(config)
    data_ingestion.run()