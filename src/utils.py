import json
import logging
import time

from openai.types.chat import ChatCompletionMessage


class DirectReturnException(Exception):
    def __init__(self, message: str | dict):
        self.message = message

    def __str__(self):
        return f"DirectReturnException(message={self.message})"

    def __repr__(self):
        return f"DirectReturnException(message={self.message!r})"


def handle_function_calls(
    function_map: dict, response_message: ChatCompletionMessage, messages: list[dict]
):
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        if function_name in function_map:
            function_args = json.loads(tool_call.function.arguments)
            print(f"Function arguments: {function_args}")

            # Call the function using the mapping
            function_to_call = function_map[function_name]
            response = function_to_call(**function_args)

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(response),
                }
            )
            return messages
        else:
            print(f"Function {function_name} not found.")


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
