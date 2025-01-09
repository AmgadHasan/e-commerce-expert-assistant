import os

import openai

from src.utils import create_logger, log_execution_time

EMBEDDING_URL = os.environ.get("EMBEDDING_URL", "https://api.jina.ai/v1")
EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY", "dumb_key")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "jina-embeddings-v3")
EMBEDDING_BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "16"))


logger = create_logger(logger_name="embedding", log_file="api.log", log_level="info")


def batch_embed(
    texts: list[str], task: str = None, batch_size: int = EMBEDDING_BATCH_SIZE
) -> list[list[float]]:
    """
    Generate embeddings for a batch of text strings.

    Args:
        texts (list[str]): A list of text strings to be embedded.
        task (str, optional): Specific task the embeddings are intended for. Defaults to None.
        batch_size (int, optional): The number of text strings to process in each batch. Defaults to EMBEDDING_BATCH_SIZE.

    Returns:
        list[list[float]]: A list of embeddings, where each embedding corresponds to a text string and consists of a list of floats.
    """
    embedding_client = openai.OpenAI(base_url=EMBEDDING_URL, api_key=EMBEDDING_API_KEY)

    result = []

    # Process texts in batches
    for i in range(0, len(texts), batch_size):
        batch_input = texts[i : i + batch_size]
        response = embedding_client.embeddings.create(
            input=batch_input, model=EMBEDDING_MODEL
        )

        # Extract and accumulate embeddings from the response.
        result.extend(x.embedding for x in response.data)

    return result


@log_execution_time(logger=logger)
def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """
    Create embeddings for a list of document chunks.

    Args:
        texts (list[str]): A list of text strings to be embedded.

    Returns:
        list[list[float]]: A list of embeddings, where each embedding is a list of floats.
    """
    return batch_embed(texts=chunks, task="retrieval.passage")


@log_execution_time(logger=logger)
def embed_query(query: str) -> list[float]:
    """
    Generate an embedding for a single query string.

    Args:
        query (str): The query text to be embedded.

    Returns:
        list[float]: The embedding for the query, represented as a list of floats.
    """
    batch_embeddings = batch_embed(texts=[query], task="retrieval.query")
    return batch_embeddings[0]
