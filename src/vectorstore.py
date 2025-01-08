import os

from qdrant_client import QdrantClient

from src.emb import embed_query
from src.utils import create_logger, log_execution_time, query_product_database

COLLECTION_NAME = "products_information"

logger = create_logger(logger_name="vectorstore", log_file="api.log", log_level="info")


def get_qdrant_client() -> QdrantClient:
    QDRANT_URL = os.environ.get(
        "QDRANT_URL",
        "https://a15c0e2e-c3d5-4404-add5-4042e47fbb25.europe-west3-0.gcp.cloud.qdrant.io:6333",
    )
    client = QdrantClient(url=QDRANT_URL, api_key=os.environ.get("QDRANT_API_KEY"))
    return client


@log_execution_time(logger=logger)
def retrieve_relevant_products(query: str) -> list[dict]:
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
        print(asins)
        logger.info(f"Retrieved {len(asins)} relevant chunks.")
        if not asins:
            logger.info("No relevant ASINs found.")
            return []

        # Use parameterized query to prevent SQL injection
        retrieved_chunks = query_product_database(
            sql_query= f"""SELECT * FROM products WHERE parent_asin IN {tuple(asins)}"""
        )
        ## Note
        # This code is used due to the sever rate limits in the LLM providers that we're using.
        # Remove this when switching to a production LLM service
        # Start
        import time
        time.sleep(62)
        retrieved_chunks = retrieved_chunks[:3]
        # End
        
        return retrieved_chunks
    except Exception as e:
        logger.exception(f"Failed to retrieve relevant context: {e}")
        raise
    finally:
        vectorstore_client.close()

# def get_qdrant_client() -> QdrantClient:
# QDRANT_URL = os.environ.get(
#     "QDRANT_URL",
#     "https://a15c0e2e-c3d5-4404-add5-4042e47fbb25.europe-west3-0.gcp.cloud.qdrant.io:6333",
# )
# client = QdrantClient(url=QDRANT_URL, api_key=os.environ.get("QDRANT_API_KEY"))
#     try:
#         yield client
#     finally:
#         client.close()


# @log_execution_time(logger=logger)
# def retrieve_relevant_products(
#     query: str, client: QdrantClient
# ) -> list[str]:
#     try:
#         query_embeddings = embed_query(query=query)
#         search_result = client.query_points(
#             collection_name=COLLECTION_NAME,
#             query=query_embeddings,
#             with_payload=True,
#             limit=10,
#         ).points
#         logger.debug(f"{search_result=}")
#         asins = [point.payload["parent_asin"] for point in search_result]
#         print(asins)
#         logger.info(f"Retrieved {len(asins)} relevant chunks.")
#         retrieved_chunks = query_product_database(
#             f"""SELECT * FROM products WHERE parent_asin IN {tuple(asins)}"""
#         )
#         return retrieved_chunks
#     except Exception as e:
#         logger.exception(f"failed to retrieve relecant context: {e}")
#         raise
