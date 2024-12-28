from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.utils.router import CentralController
from app.utils.storage_utils import initialize_qdrant_client
from config import (
    QDRANT_API_KEY, QDRANT_URL, ENVIRONMENT,
    CORS_ORIGINS, ChatContext, QueryResponse,
    ORIGIN
)

load_dotenv()

app = FastAPI()

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = ORIGIN
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Initialize Qdrant client
client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY, ENVIRONMENT)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(chatContext: ChatContext):
    if not chatContext.messages:
        raise HTTPException(status_code=400, detail="Query text is required.")
    
    central_controller = CentralController(
        model_type=chatContext.model_type,
        huggingface_model_name=chatContext.huggingface_model_name
    )
    
    result = await central_controller.process_query(
        client, chatContext.messages
    )
    
    if not result or "answer" not in result or "sources" not in result:
        return QueryResponse(
            answer="Sorry, but it seems there was an error with my database. Please try again later.",
            sources=[],
        )
    
    return QueryResponse(answer=result["answer"], sources=result["sources"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Germany Study Info API"}