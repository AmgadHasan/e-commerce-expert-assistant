import json
import logging
import os
import time
from pathlib import Path

import src.models as models

import sqlite3
from contextlib import closing


def query_product_database(sql_query: str, db_url: str = "data/products_information.db"):
    with closing(sqlite3.connect(f'file:{db_url}?mode=ro', uri=True)) as connection:
        connection.row_factory = lambda cursor, row: {col[0]: row[i] for i, col in enumerate(cursor.description)}
        with closing(connection.cursor()) as cursor:
            rows = cursor.execute(sql_query).fetchall()            
    return rows

class DirectReturnException(Exception):
    def __init__(self, message: str | dict):
        self.message = message

    def __str__(self):
        return f"DirectReturnException(message={self.message})"

    def __repr__(self):
        return f"DirectReturnException(message={self.message!r})"


def handle_function_calls(
    function_map: dict, response_message, messages: list[models.Message | dict]
) -> list[models.Message | dict] | None:
    if not response_message.tool_calls:
        raise
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        if function_name in function_map:
            function_args = json.loads(tool_call.function.arguments)
            print(f"Function arguments: {function_args}")

            function_to_call = function_map[function_name]
            function_response = function_to_call(**function_args)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )
            return messages
        else:
            print(f"Function {function_name} not found.")
            raise


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


def load_env_file(env_file_path: Path):
    """
    Load environment variables from a .env file and add them to os.environ.

    :param env_file_path: Path to the .env file
    :type env_file_path: str
    """
    try:
        with open(env_file_path, "r") as env_file:
            for line in env_file:
                # Strip whitespace and ignore empty lines and comments
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Split the line into key and value
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"Error: The file at {env_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
