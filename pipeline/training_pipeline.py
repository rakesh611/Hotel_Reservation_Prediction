import os
from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataProcessor
from src.model_training import ModelTraining
from src.logger import get_logger
from src.custom_exception import CustomException
from utils.common_functions import read_yaml
from config.paths_config import *

logger = get_logger(__name__)


def run_pipeline():
    try:
        logger.info("========== PIPELINE STARTED ==========")

        # ✅ Load config once
        config = read_yaml(CONFIG_PATH)

        # =========================
        # 1. Data Ingestion
        # =========================
        logger.info("Starting Data Ingestion")
        data_ingestion = DataIngestion(config)
        data_ingestion.run()

        # =========================
        # 2. Data Processing
        # =========================
        logger.info("Starting Data Preprocessing")
        processor = DataProcessor(
            TRAIN_FILE_PATH,
            TEST_FILE_PATH,
            PROCESSED_DIR,
            CONFIG_PATH
        )
        processor.process()

        # =========================
        # 3. Model Training
        # =========================
        logger.info("Starting Model Training")
        trainer = ModelTraining(
            PROCESSED_TRAIN_DATA_PATH,
            PROCESSED_TEST_DATA_PATH,
            MODEL_OUTPUT_PATH
        )
        trainer.run()

        logger.info("========== PIPELINE COMPLETED SUCCESSFULLY ==========")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise CustomException("Pipeline execution failed", e)


if __name__ == "__main__":
    run_pipeline()