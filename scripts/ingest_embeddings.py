import argparse
import os
from pathlib import Path

import openai
import polars as pl
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams

from src.utils import create_logger, log_execution_time
from src.emb import embed_chunks

COLLECTION_NAME = "products_information_02"


logger = create_logger(logger_name="script", log_file="api.log", log_level="info")


@log_execution_time(logger=logger)
def ingest_dataset(
    dataset_file: Path, client: QdrantClient, embedding_dimension: int
) -> None:
    """
    Ingest a dataset parquet file into Qdrant by creating a collection, embedding text into vectors,
    and upserting them into the collection.

    Args:
        dataset_file (Path): Path to the dataset parquet file.
        client (QdrantClient): Instance of the QdrantClient to interact with the vectordb.
        embedding_dimension (int): Dimensionality of the embedding vectors.
    """
    if client.collection_exists(collection_name=COLLECTION_NAME):
        logger.info("Collection already exists! Skipping embedding and insertion.")
        return

    # Create a new collection within Qdrant
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=embedding_dimension, distance=Distance.DOT),
    )

    # Read data from the parquet and prepare for processing
    dataset = pl.read_parquet(dataset_file).with_row_index("id")
    for i in range(0, dataset.shape[0], 64):
        batch_df = dataset[i : i + 64]
        text_chunks = (batch_df["features"] + batch_df["title"]).to_list()
        embedding_vectors = embed_chunks(chunks=text_chunks)

        # Attempt to upsert vectors into the Qdrant collection
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=models.Batch(
                    ids=batch_df["id"].to_list(),
                    payloads=[
                        {"parent_asin": parent_asin, "title": title}
                        for title, parent_asin in batch_df[
                            ["title", "parent_asin"]
                        ].iter_rows()
                    ],
                    vectors=embedding_vectors,
                ),
            )
            logger.info(
                f"Generated {len(text_chunks)} chunks and upserted into vectordb."
            )
        except Exception as e:
            logger.exception(f"Failed to upsert: {e}")
            raise


def parse_arguments():
    """
    Parse command-line arguments for configuring dataset ingestion.

    Returns:
        args: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Ingest dataset into Qdrant vectordb.")

    parser.add_argument(
        "--qdrant-url",
        type=str,
        default=os.environ.get(
            "QDRANT_URL",
            "https://a15c0e2e-c3d5-4404-add5-4042e47fbb25.europe-west3-0.gcp.cloud.qdrant.io:6333",
        ),
        help="The connection URL for the Qdrant vector DB.",
    )
    parser.add_argument(
        "--embedding-dimension",
        type=int,
        default=os.environ.get("EMBEDDING_DIMENSION", 1024),
        help="The dimension of the embedding vectors.",
    )
    parser.add_argument(
        "--openai-base-url",
        type=str,
        default=os.environ.get("OPENAI_BASE_URL", "http://localhost:8000/v1"),
        help="The base URL for the OpenAI API.",
    )
    parser.add_argument(
        "--openai-api-key",
        type=str,
        default=os.environ.get("OPENAI_API_KEY"),
        help="The API key for the OpenAI API.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    vectordb_client = QdrantClient(
        url=args.qdrant_url, api_key=os.environ.get("QDRANT_API_KEY")
    )
    emb_client = openai.OpenAI(
        base_url=args.openai_base_url, api_key=args.openai_api_key
    )

    ingest_dataset(
        dataset_file=Path("data/product_information.parquet"),
        client=vectordb_client,
        embedding_dimension=args.embedding_dimension,
    )
