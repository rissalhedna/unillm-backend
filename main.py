from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.utils.router import CentralController
from app.utils.storage_utils import initialize_qdrant_client
from config import (
    QDRANT_API_KEY, QDRANT_URL, ENVIRONMENT, ChatContext, QueryResponse,
    ORIGIN, CORS_ORIGINS
)
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        ORIGIN,
        "https://unillm-rissals-projects.vercel.app",
        "https://unillm-frontend-git-main-rissals-projects.vercel.app/"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(chatContext: ChatContext):
    if not chatContext.messages:
        raise HTTPException(status_code=400, detail="Query text is required.")
    
    central_controller =    CentralController(
        model_type=chatContext.model_type,
        huggingface_model_name=chatContext.huggingface_model_name
    )
    
    result = await central_controller.process_query(
        client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY, ENVIRONMENT), messages=chatContext.messages
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

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin")
    if origin and origin in CORS_ORIGINS:
        headers = {"Access-Control-Allow-Origin": origin}
    else:
        headers = {"Access-Control-Allow-Origin": ORIGIN}  # Default origin
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
        headers=headers
    )
