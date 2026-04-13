import os
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml, load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)


class DataProcessor:

    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir

        self.config = read_yaml(config_path)

        os.makedirs(self.processed_dir, exist_ok=True)

    # =========================
    # Preprocessing
    # =========================
    def preprocess_data(self, df):
        try:
            logger.info("Starting Data Preprocessing")

            # ✅ SAFE DROP (FIXED ERROR)
            df.drop(columns=['Unnamed: 0', 'Booking_ID'], errors='ignore', inplace=True)

            # Remove duplicates
            df.drop_duplicates(inplace=True)

            cat_cols = self.config["data_processing"]["categorical_columns"]
            num_cols = self.config["data_processing"]["numerical_columns"]

            # =========================
            # Label Encoding
            # =========================
            logger.info("Applying Label Encoding")

            mappings = {}

            for col in cat_cols:
                if col in df.columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col])

                    mappings[col] = dict(
                        zip(le.classes_, le.transform(le.classes_))
                    )

            logger.info(f"Label mappings: {mappings}")

            # =========================
            # Skewness Handling
            # =========================
            logger.info("Handling skewness")

            skew_threshold = self.config["data_processing"]["skewness_threshold"]

            existing_num_cols = [col for col in num_cols if col in df.columns]

            skewness = df[existing_num_cols].apply(lambda x: x.skew())

            for col in skewness[skewness > skew_threshold].index:
                df[col] = np.log1p(df[col])

            return df

        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            raise CustomException("Error while preprocessing data", e)

    # =========================
    # SMOTE
    # =========================
    def balance_data(self, df):
        try:
            logger.info("Applying SMOTE")

            if "booking_status" not in df.columns:
                raise Exception("Target column 'booking_status' missing")

            X = df.drop(columns='booking_status')
            y = df['booking_status']

            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)

            balanced_df = pd.DataFrame(X_resampled, columns=X.columns)
            balanced_df["booking_status"] = y_resampled

            logger.info("Data balanced successfully")

            return balanced_df

        except Exception as e:
            logger.error(f"Error during SMOTE: {e}")
            raise CustomException("Error while balancing data", e)

    # =========================
    # Feature Selection
    # =========================
    def select_features(self, df):
        try:
            logger.info("Starting Feature Selection")

            X = df.drop(columns='booking_status')
            y = df['booking_status']

            model = RandomForestClassifier(random_state=42)
            model.fit(X, y)

            feature_importance = model.feature_importances_

            feature_df = pd.DataFrame({
                "feature": X.columns,
                "importance": feature_importance
            }).sort_values(by="importance", ascending=False)

            n_features = self.config["data_processing"]["no_of_features"]

            top_features = feature_df["feature"].head(n_features).tolist()

            logger.info(f"Selected features: {top_features}")

            final_df = df[top_features + ["booking_status"]]

            return final_df

        except Exception as e:
            logger.error(f"Error during feature selection: {e}")
            raise CustomException("Error while feature selection", e)

    # =========================
    # Save Data
    # =========================
    def save_data(self, df, path):
        try:
            df.to_csv(path, index=False)
            logger.info(f"Data saved at {path}")

        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise CustomException("Error while saving data", e)

    # =========================
    # Pipeline Execution
    # =========================
    def process(self):
        try:
            logger.info("Loading raw data")

            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            # Preprocess
            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            # Balance
            train_df = self.balance_data(train_df)
            test_df = self.balance_data(test_df)

            # Feature selection
            train_df = self.select_features(train_df)

            # Align test data columns
            test_df = test_df[train_df.columns]

            # Save
            self.save_data(train_df, PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH)

            logger.info("Data Processing Completed Successfully")

        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {e}")
            raise CustomException("Error in data preprocessing pipeline", e)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    processor = DataProcessor(
        TRAIN_FILE_PATH,
        TEST_FILE_PATH,
        PROCESSED_DIR,
        CONFIG_PATH
    )
    processor.process()