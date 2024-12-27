import logging

from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant.base import QdrantVectorStore
from qdrant_client import QdrantClient

from constants import MAX_SOURCES

logger = logging.getLogger(__name__)

def query_qdrant(client, collection_name, query):
    if not _test_qdrant_connection(client):
        return {
            "answer": "Database connection failed. Please ensure Qdrant server is running.",
            "sources": [],
        }

    try:
        vector_store = QdrantVectorStore(
            client=client, collection_name=collection_name, prefer_grpc=True
        )
        collection_info = client.get_collection(collection_name)
        logger.info(f"Collection info: {collection_info}")

        index = VectorStoreIndex.from_vector_store(vector_store)
        nodes = _retrieve_nodes(index, query)

        if not nodes:
            logger.warning("No source nodes found")
            return {"context": "", "sources": []}

        return _process_retrieved_nodes(nodes)

    except Exception as e:
        logger.error(f"Error during query processing: {e}", exc_info=True)
        return {"error": "Query processing failed", "details": str(e)}


def _test_qdrant_connection(client) -> bool:
    try:
        client.get_collections()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return False


def _retrieve_nodes(index, query) -> list:
    retriever = index.as_retriever(similarity_top_k=MAX_SOURCES, filters=None)
    return retriever.retrieve(query)


def _process_retrieved_nodes(nodes: list) -> dict:
    context_text = "\n\n".join([node.node.text for node in nodes])
    unique_sources = _filter_unique_sources(nodes)
    return {"context": context_text, "sources": unique_sources}


def _filter_unique_sources(nodes: list) -> list:
    seen_urls = set()
    unique_sources = []
    for node in sorted(
        nodes, key=lambda x: x.score if hasattr(x, "score") else 0, reverse=True
    ):
        url = node.node.metadata.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(node.node.metadata)
    return unique_sources


def initialize_qdrant_client(url, api_key, environment):
    try:
        return QdrantClient(host="localhost", port=6333) if environment == "dev" else QdrantClient(url, api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Error initializing Qdrant client: {str(e)}")
