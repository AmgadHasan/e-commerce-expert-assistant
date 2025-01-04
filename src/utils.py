import logging
import time


def create_logger(logger_name, log_file, log_level):
    LOG_FORMAT = "[%(asctime)s | %(name)s | %(levelname)s | %(message)s]"
    log_level = getattr(logging, log_level.upper())

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)

    return logger


def log_execution_time(logger):
    """Decorator factory to log the execution time of a function using a specified logger."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Executing {func.__name__} took {execution_time:.4f} seconds")
            return result

        return wrapper

    return decorator
