from noobTunerLLM.logger import logger

# Example usage
def train_model():
    try:
        logger.info("Starting model training...")
        # Your training code here
        logger.info("Model training completed successfully")
        print("Model training completed successfully")
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise

def preprocess_data():
    logger.info("Starting data preprocessing...")
    # Your preprocessing code
    logger.debug("Preprocessing step ")

    print("Preprocessing step ")



train_model()
preprocess_data()

