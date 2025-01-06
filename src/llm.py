import os

from openai import OpenAI

from src.prompts import (
    ORDER_SYSTEM_MESSAGE,
)
from src.tools import order_dataset_tools, order_function_map
from src.utils import create_logger, handle_function_calls, log_execution_time

TEMPERATURE = 0
MAX_COMPLETION_TOKENS = 2048

logger = create_logger(logger_name="llm", log_file="api.log", log_level="info")

model = os.environ.get("CHAT_MODEL")
if not model:
    logger.error("CHAT_MODEL environment variable is not set.")
    raise ValueError("CHAT_MODEL environment variable is not set.")

client = OpenAI()


# def prepare_context(relevant_chunks: list[str]) -> str:
#     """
#     Prepare the input context for the summarization model.
#     Args:
#         relevant_chunks (List[str]): A list of text chunks relevant to the topic.
#     Returns:
#         str: The concatenated text of the relevant chunks.
#     """
#     # This can be improved for prompt engineering!
#     return "\n".join(relevant_chunks)


@log_execution_time(logger=logger)
def handle_user_chat(messages: list[dict]) -> dict:
    """
    Generate responses for a given user query.

    Args:
        query (str): The main topic to be asked about.
        relevant_chunks (list[str]): A list of text chunks relevant to the topic.

    Returns:
        list[str]: A list of questions about the topic based on the provided context.
    """
    input_messages = messages
    try:
        while True:
            print(f"Inside loop{messages[-1]}")
            response = create_completition(messages=messages)
            messages.append(response)
            print(response)
            if not response.tool_calls:
                print("No tool call")
                break
            messages = handle_function_calls(
                function_map=order_function_map,
                response_message=response,
                messages=messages,
            )
        return {"role": response.role, "content": response.content}
    except Exception as e:
        logger.error(
            f"Error generating responses for chat:\n'{input_messages}'\n\nError:\n{e}"
        )
        raise


@log_execution_time(logger=logger)
def create_completition(
    messages: list[dict], system_message: str = ORDER_SYSTEM_MESSAGE
):
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                *messages,
            ],
            model=model,
            temperature=TEMPERATURE,
            max_tokens=MAX_COMPLETION_TOKENS,
            tools=order_dataset_tools,
        )
        print(f"{completion = }")
        response = completion.choices[0].message
        print(f"Inside create completitions: {messages[-1]}\n\n\n{response}")
        return response
    except Exception as e:
        logger.error(f"Error generating responses for chat '{messages}': {e}")
        raise
