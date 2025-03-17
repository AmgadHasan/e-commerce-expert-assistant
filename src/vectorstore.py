import os

from qdrant_client import QdrantClient

from src.emb import embed_query
from src.utils import create_logger, log_execution_time, query_product_database

COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "products_information")

logger = create_logger(logger_name="vectorstore", log_file="api.log", log_level="info")


def get_qdrant_client() -> QdrantClient:
    """
    Initialize and return a Qdrant client using provided configuration from environment variables.

    Returns:
        QdrantClient: An instance of QdrantClient connected to the specified Qdrant server.
    """
    QDRANT_URL = os.environ.get(
        "QDRANT_URL",
        "https://a15c0e2e-c3d5-4404-add5-4042e47fbb25.europe-west3-0.gcp.cloud.qdrant.io:6333",
    )
    client = QdrantClient(url=QDRANT_URL, api_key=os.environ.get("QDRANT_API_KEY"))
    return client


@log_execution_time(logger=logger)
def retrieve_relevant_products(query: str) -> list[dict]:
    """
    Retrieve the most relevant products to a given query using Qdrant vector search
    and then fetch additional details from the product database.

    Args:
        query (str): The search query for which relevant products are to be retrieved.

    Returns:
        list[dict]: A list of dictionaries containing detailed information of relevant products.
    """
    vectorstore_client = get_qdrant_client()
    try:
        query_embeddings = embed_query(query=query)
        search_result = vectorstore_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embeddings,
            with_payload=True,
            limit=10,
        ).points
        logger.debug(f"{search_result=}")
        asins = [point.payload["parent_asin"] for point in search_result]
        logger.info(f"Retrieved {len(asins)} relevant chunks.")
        if not asins:
            logger.info("No relevant ASINs found.")
            return []

        # Fetch product details from the database using the retrieved ASINs
        retrieved_chunks = query_product_database(
            sql_query=f"SELECT * FROM products WHERE parent_asin IN {tuple(asins)}"
        )

        # Throttle LLM request rate (remove this in production)
        ## Begin
        import time

        time.sleep(62)
        retrieved_chunks = retrieved_chunks[:3]
        ## End

        return retrieved_chunks
    except Exception as e:
        logger.exception(f"Failed to retrieve relevant context: {e}")
        raise
    finally:
        vectorstore_client.close()
