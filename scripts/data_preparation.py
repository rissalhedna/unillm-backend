import json
import logging
from typing import Optional
from llama_cloud import SentenceSplitter
from llama_index.core import StorageContext
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant.base import QdrantVectorStore
from transformers import AutoModel, AutoTokenizer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from constants import CHUNK_OVERLAP, CHUNK_SIZE, QDRANT_EMBEDDING_MODEL

logger = logging.getLogger(__name__)

def store_in_qdrant(
    client,
    collection_name: Optional[str] = "study-in-germany",
    file_path: Optional[str] = "./data/",
):
    data = _load_data(file_path)
    documents = _create_documents(data)
    vector_store = _initialize_vector_store(client, collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    _configure_settings()
    _store_documents(documents, storage_context)
    logger.info("Data stored in Qdrant!")

def _load_data(file_path: str) -> list:
    logging.info(f"Loading data from {file_path}")
    with open(file_path, "r") as f:
        return json.load(f)

def _create_documents(data: list) -> list:
    return [Document(text=entry["text"], metadata=entry["metadata"]) for entry in data]

def _initialize_vector_store(client, collection_name: str) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=str(collection_name),
        batch_size=50,
        prefer_grpc=True,
        metadata_config={
            "url": "keyword",
            "title": "keyword",
            "source_type": "keyword",
            "date_added": "keyword",
        },
    )

def _configure_settings(model_type: str = "openai", huggingface_model_name: Optional[str] = None):
    if model_type == "openai":
        Settings.embed_model = OpenAIEmbedding(model=QDRANT_EMBEDDING_MODEL)
    elif model_type == "huggingface" and huggingface_model_name:
        tokenizer = AutoTokenizer.from_pretrained(huggingface_model_name)
        model = AutoModel.from_pretrained(huggingface_model_name)
        Settings.embed_model = HuggingFaceEmbedding(model=model, tokenizer=tokenizer)
    else:
        raise ValueError("Invalid model type or missing Hugging Face model name")

def _store_documents(documents: list, storage_context: StorageContext):
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

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
        text_splitter=text_splitter,
    ) 