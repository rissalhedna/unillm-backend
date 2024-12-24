import os
from typing import List, Optional

import qdrant_client
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.utils.router import CentralController
from app.utils.storage_utils import query_qdrant, store_in_qdrant

load_dotenv()

app = FastAPI()

# Define the origins that should be allowed to make cross-origin requests
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies to be sent in cross-origin requests
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT")

if not QDRANT_API_KEY or not QDRANT_URL or not ENVIRONMENT:
    raise RuntimeError(
        "Missing required environment variables: QDRANT_API_KEY, QDRANT_URL, ENVIRONMENT"
    )

try:
    if ENVIRONMENT == "dev":
        client = qdrant_client.QdrantClient(
            host="localhost",
            port=6333,
        )
    else:
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in production.")
        client = qdrant_client.QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)
except Exception as e:
    raise RuntimeError(f"Error initializing Qdrant client: {str(e)}")


class ChatContext(BaseModel):
    messages: List[dict]
    collection_name: Optional[str] = "study-in-germany"


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]


class StoreRequest(BaseModel):
    collection_name: Optional[str] = "study-in-germany"
    directory_name: Optional[str] = None


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(chatContext: ChatContext):
    if not chatContext.messages:
        raise HTTPException(status_code=400, detail="Query text is required.")
    central_controller = CentralController()
    result = await central_controller.process_query(client, chatContext.messages, query_qdrant)
    if not result or "answer" not in result or "sources" not in result:
        return QueryResponse(
            answer="Sorry, but it seems there was an error with my database. Please try again later.",
            sources=[],
        )
    return QueryResponse(answer=result["answer"], sources=result["sources"])


@app.post("/store", status_code=201)
async def store_endpoint(request: StoreRequest):
    if not request.collection_name:
        raise HTTPException(status_code=400, detail="Collection name is required.")
    try:
        store_in_qdrant(client, request.collection_name, request.directory_name)
        return {"message": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred while storing data: {str(e)}"
        )


@app.get("/")
async def root():
    return {"message": "Welcome to the Germany Study Info API"}


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        raise RuntimeError(f"Failed to start FastAPI application: {str(e)}")