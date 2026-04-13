import os
import joblib
import lightgbm as lgb
import pandas as pd

from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import load_data

import mlflow
import mlflow.sklearn

logger = get_logger(__name__)


class ModelTraining:

    def __init__(self, train_path, test_path, model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

        # ✅ FAST + STABLE PARAMS (reduced search space)
        self.params_dist = {
            "num_leaves": [31, 50],
            "max_depth": [-1, 5],
            "learning_rate": [0.05, 0.1],
            "n_estimators": [50, 100],
        }

        # ✅ Reduce training time (IMPORTANT)
        self.random_search_params = {
            "n_iter": 5,          # 🔥 reduced from 10/20
            "cv": 3,              # 🔥 reduced CV
            "n_jobs": -1,
            "verbose": 1,
            "random_state": 42,
            "scoring": "f1"
        }

    def load_and_split_data(self):
        try:
            logger.info("Loading training data")
            train_df = load_data(self.train_path)

            logger.info("Loading testing data")
            test_df = load_data(self.test_path)

            # ✅ Drop constant columns (fix LightGBM warning)
            nunique = train_df.nunique()
            constant_cols = nunique[nunique == 1].index.tolist()

            if constant_cols:
                logger.info(f"Dropping constant columns: {constant_cols}")
                train_df.drop(columns=constant_cols, inplace=True, errors="ignore")
                test_df.drop(columns=constant_cols, inplace=True, errors="ignore")

            X_train = train_df.drop(columns=["booking_status"])
            y_train = train_df["booking_status"]

            X_test = test_df.drop(columns=["booking_status"])
            y_test = test_df["booking_status"]

            logger.info("Data split successfully")

            return X_train, y_train, X_test, y_test

        except Exception as e:
            logger.error(f"Error while loading data: {e}")
            raise CustomException("Failed to load data", e)

    def train_lgbm(self, X_train, y_train):
        try:
            logger.info("Initializing LightGBM model")

            model = lgb.LGBMClassifier(
                random_state=42,
                force_col_wise=True,   # ✅ removes threading warning
                verbosity=-1           # ✅ removes log spam
            )

            logger.info("Starting hyperparameter tuning (FAST MODE)")

            random_search = RandomizedSearchCV(
                estimator=model,
                param_distributions=self.params_dist,
                n_iter=self.random_search_params["n_iter"],
                cv=self.random_search_params["cv"],
                n_jobs=self.random_search_params["n_jobs"],
                verbose=self.random_search_params["verbose"],
                random_state=self.random_search_params["random_state"],
                scoring=self.random_search_params["scoring"]
            )

            random_search.fit(X_train, y_train)

            best_model = random_search.best_estimator_
            logger.info(f"Best Parameters: {random_search.best_params_}")

            return best_model

        except Exception as e:
            logger.error(f"Error while training model: {e}")
            raise CustomException("Failed to train model", e)

    def evaluate_model(self, model, X_test, y_test):
        try:
            logger.info("Evaluating model")

            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)

            logger.info(f"Accuracy: {accuracy}")
            logger.info(f"Precision: {precision}")
            logger.info(f"Recall: {recall}")
            logger.info(f"F1 Score: {f1}")

            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }

        except Exception as e:
            logger.error(f"Error while evaluating model: {e}")
            raise CustomException("Failed to evaluate model", e)

    def save_model(self, model, X_train):
        try:
            os.makedirs(os.path.dirname(self.model_output_path), exist_ok=True)

            # ✅ Save model
            joblib.dump(model, self.model_output_path)
            logger.info(f"Model saved to {self.model_output_path}")

            # ✅ Save feature order (CRITICAL for Flask)
            feature_path = os.path.join(
                os.path.dirname(self.model_output_path),
                "features.pkl"
            )
            joblib.dump(X_train.columns.tolist(), feature_path)

            logger.info(f"Feature list saved to {feature_path}")

        except Exception as e:
            logger.error(f"Error while saving model: {e}")
            raise CustomException("Failed to save model", e)

    def run(self):
        try:
            logger.info("Starting Model Training Pipeline")

            with mlflow.start_run():

                # ✅ Log dataset safely
                if os.path.exists(self.train_path):
                    mlflow.log_artifact(self.train_path, artifact_path="datasets")

                if os.path.exists(self.test_path):
                    mlflow.log_artifact(self.test_path, artifact_path="datasets")

                # Load data
                X_train, y_train, X_test, y_test = self.load_and_split_data()

                # Train
                model = self.train_lgbm(X_train, y_train)

                # Evaluate
                metrics = self.evaluate_model(model, X_test, y_test)

                # Save model
                self.save_model(model, X_train)

                # Log model
                mlflow.sklearn.log_model(model, "model")

                # Log params & metrics
                mlflow.log_params(model.get_params())
                mlflow.log_metrics(metrics)

                logger.info("Model Training completed successfully")

        except Exception as e:
            logger.error(f"Error in model training pipeline: {e}")
            raise CustomException("Failed during model training pipeline", e)


if __name__ == "__main__":
    trainer = ModelTraining(
        PROCESSED_TRAIN_DATA_PATH,
        PROCESSED_TEST_DATA_PATH,
        MODEL_OUTPUT_PATH
    )
    trainer.run()