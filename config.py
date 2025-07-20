import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel

load_dotenv()

# Default Model and Collection
DEFAULT_COLLECTION_NAME = "study-in-germany"
DEFAULT_MODEL_TYPE = "openai"
DEFAULT_HUGGINGFACE_MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"


class ChatContext(BaseModel):
    messages: List[dict]
    collection_name: Optional[str] = "study-in-germany"
    model_name: Optional[str] = "gpt-4"
    temperature: Optional[float] = 0.0

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

# Environment Variables
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")
ORIGIN = os.getenv("ORIGIN")