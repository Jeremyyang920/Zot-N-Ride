import logging

def configure_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("logger.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt="[%(levelname)s] %(asctime)s: %(message)s", datefmt="%Y-%m-%d, %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
