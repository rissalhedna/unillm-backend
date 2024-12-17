import logging
from typing import Optional

from llama_cloud import SentenceSplitter
from llama_index.core import PromptTemplate, SimpleDirectoryReader, StorageContext
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant.base import QdrantVectorStore

logger = logging.getLogger(__name__)

CHUNK_SIZE = 256
CHUNK_OVERLAP = 20
SIMILARITY_TOP_K = 5
SIMILARITY_CUTOFF = 0.7


def store_in_qdrant(
    client,
    collection_name: Optional[str] = "study-in-germany",
    file_path: Optional[str] = "./data/",
):
    max_files = 10
    logging.info(
        f"Parsing through the {file_path} file. MAXIMUM {max_files} files to be uploaded (Change that argument in the function body)"
    )
    documents = SimpleDirectoryReader(
        input_files=[file_path],
        file_metadata=lambda path: {"file_name": path.split("/")[-1]},
    ).load_data()

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=str(collection_name),
        batch_size=100,
        prefer_grpc=True,
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

    embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    llm = OpenAI(model="gpt-4o-mini")

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

        index = VectorStoreIndex.from_vector_store(vector_store)

        # Define your custom prompt template
        custom_prompt_template = PromptTemplate(
            "You are an AI assistant tasked with answering questions based on the given context. "
            "Use the following pieces of context to answer the question at the end. "
            "You will give the most detailed possible answers to help prospective students find the necessary"
            "information about living and/or studying in Germany."
            "If you don't know the answer, just say that you don't know, don't try to make up an answer. "
            "----------------\n"
            "{context_str}\n"
            "----------------\n"
            "Question: {query_str}\n"
            "Answer: "
        )

        # Create a retriever from the index
        retriever = index.as_retriever(similarity_top_k=10)

        # Create the query engine with the custom prompt
        query_engine = RetrieverQueryEngine.from_args(
            retriever, text_qa_template=custom_prompt_template, verbose=True
        )

        # Execute the query
        response = query_engine.query(query)

        return {
            "answer": str(response),
            "sources": [node.metadata for node in response.source_nodes],
        }
    except Exception as e:
        logger.error(f"Error during query processing: {e}")
        return {"error": "Query processing failed", "details": str(e)}
