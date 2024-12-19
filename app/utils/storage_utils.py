import logging
from typing import Optional
import json

from llama_cloud import SentenceSplitter
from llama_index.core import PromptTemplate, StorageContext
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant.base import QdrantVectorStore
from llama_index.core.schema import Document
from qdrant_client.http import models
from llama_index.core.postprocessor.node import SimilarityPostprocessor, KeywordNodePostprocessor

logger = logging.getLogger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
SIMILARITY_TOP_K = 10
SIMILARITY_CUTOFF = 0


def store_in_qdrant(
    client,
    collection_name: Optional[str] = "study-in-germany",
    file_path: Optional[str] = "./data/",
):
    logging.info(f"Loading data from {file_path}")
    
    # Load JSON instead of txt
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Create Document objects with metadata
    documents = []
    for entry in data:
        doc = Document(
            text=entry['text'],
            metadata=entry['metadata']
        )
        documents.append(doc)

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=str(collection_name),
        batch_size=100,
        prefer_grpc=True,
        metadata_config={
            "url": "keyword",
            "title": "keyword",
            "source_type": "keyword",
            "date_added": "keyword"
        }
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP

    text_splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        include_metadata=True,
        include_prev_next_rel=False,
        callback_manager=None,
        separator=" ",
        paragraph_separator="\n",
        secondary_chunking_regex=None,
        class_name=None,
    )  # type: ignore

    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    llm = OpenAI(model="gpt-4o")

    Settings.embed_model = embed_model
    Settings.llm = llm

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
        text_splitter=text_splitter,
    )
    logger.info("Data stored in Qdrant!")


def query_qdrant(client, collection_name, query):
    try:
        # Test connection first
        client.get_collections()
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return {
            "error": "Database connection failed. Please ensure Qdrant server is running.",
            "details": str(e),
        }

    try:
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            prefer_grpc=True,
        )

        # Add logging to check if vector store has content
        collection_info = client.get_collection(collection_name)
        logger.info(f"Collection info: {collection_info}")

        index = VectorStoreIndex.from_vector_store(vector_store)
        
        # Modify retriever settings to be more lenient
        retriever = index.as_retriever(
            similarity_top_k=SIMILARITY_TOP_K,
            filters=None,
            similarity_cutoff=None,  # Remove similarity cutoff initially
        )
        custom_prompt_template = PromptTemplate(
            "You are a knowledgeable educational advisor specializing in German higher education and life in Germany. "
            "Based on the provided context, your task is to assist prospective students with accurate and comprehensive information. "
            "\nGuidelines:"
            "\n- Provide detailed, well-structured answers focusing on practical information"
            "\n- Include specific requirements, deadlines, or processes when relevant"
            "\n- Cite specific German regulations or institutions when applicable"
            "\n- Break down complex procedures into clear steps"
            "\n- If information is time-sensitive, mention that details may change"
            "\n- If the answer is not found in the context, clearly state that and suggest where to find reliable information"
            "\n----------------\n"
            "{context_str}\n"
            "----------------\n"
            "Question: {query_str}\n"
            "Answer: Let me help you with that.\n"
        )
        # Simplify the query engine configuration for testing
        query_engine = RetrieverQueryEngine.from_args(
            retriever,
            text_qa_template=custom_prompt_template,
            verbose=True,
            node_postprocessors=[],  # Remove postprocessors temporarily
        )

        # Add debug logging
        logger.info(f"Executing query: {query}")
        response = query_engine.query(query)
        logger.info(f"Raw response: {response}")
        logger.info(f"Number of source nodes: {len(response.source_nodes)}")

        # Process response only if source nodes exist
        if not response.source_nodes:
            logger.warning("No source nodes found in response")
            return {
                "answer": "No relevant information found in the database.",
                "sources": [],
                "scores": []
            }

        sorted_sources = sorted(
            response.source_nodes,
            key=lambda x: x.score if hasattr(x, 'score') else 0,
            reverse=True
        )

        return {
            "answer": str(response),
            "sources": [node.metadata for node in sorted_sources],
            "scores": [node.score if hasattr(node, 'score') else 0 for node in sorted_sources]
        }

    except Exception as e:
        logger.error(f"Error during query processing: {e}", exc_info=True)
        return {"error": "Query processing failed", "details": str(e)}


def delete_from_qdrant_by_url(client, collection_name: str, url_pattern: str):
    """
    Delete entries from Qdrant that have URLs containing the specified pattern.
    
    Args:
        client: Qdrant client instance
        collection_name (str): Name of the collection
        url_pattern (str): Pattern to match in URLs (e.g., 'handbook-germany.de')
    
    Returns:
        dict: Status of the deletion operation
    """
    try:
        # Test connection first
        client.get_collections()
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant: {e}")
        return {
            "success": False,
            "error": "Database connection failed. Please ensure Qdrant server is running.",
            "details": str(e),
        }

    try:
        # Search for matching documents using URL pattern
        search_results = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="url",
                        match=models.MatchText(text=url_pattern)  # Using MatchText for partial matches
                    )
                ]
            ),
            limit=100
        )
        
        points_found = len(search_results[0])
        logger.info(f"Found {points_found} points with URLs containing '{url_pattern}'")
        
        if points_found > 0:
            # Delete points with matching URLs
            client.delete(
                collection_name=collection_name,
                points_selector=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="url",
                            match=models.MatchText(text=url_pattern)
                        )
                    ]
                )
            )
            
            logger.info(f"Successfully deleted {points_found} entries with URLs containing '{url_pattern}'")
            return {
                "success": True,
                "message": f"Deleted {points_found} entries with URLs containing '{url_pattern}'"
            }
        else:
            logger.warning(f"No entries found with URLs containing '{url_pattern}'")
            return {
                "success": False,
                "error": "No matching entries found",
                "details": f"No entries found with URLs containing '{url_pattern}'"
            }
        
    except Exception as e:
        logger.error(f"Error deleting entries with URL pattern '{url_pattern}': {e}")
        return {
            "success": False,
            "error": "Failed to delete entries",
            "details": str(e)
        }
