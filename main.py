from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger
from app.utils.router import CentralController
from app.utils.storage_utils import initialize_qdrant_client
from config import (
    QDRANT_API_KEY, QDRANT_URL, ENVIRONMENT, ChatContext,
    ORIGIN, CORS_ORIGINS
)
from fastapi.responses import JSONResponse
import json

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


async def stream_response(stream_response, sources):
    """Convert OpenAI streaming response to our format"""
    try:
        for source in sources:
            yield f"source: {source}\n\n"
        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield content
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/query")
async def query_endpoint(chatContext: ChatContext):
    if not chatContext.messages:
        raise HTTPException(status_code=400, detail="Messages are required.")
    
    central_controller = CentralController(
        model_name=chatContext.model_name,
        temperature=chatContext.temperature
    )
    client = initialize_qdrant_client(QDRANT_URL, QDRANT_API_KEY, ENVIRONMENT)
    
    try:
        result = await central_controller.process_query(client=client, messages=chatContext.messages)
        
        if not result or "answer" not in result:
            return JSONResponse(
                content={
                    "answer": "Sorry, but it seems there was an error with my database. Please try again later.",
                    "sources": []
                }
            )
        
        sources = result.get("sources", [])
        stream_response_obj = result["answer"]
        
        return StreamingResponse(
            stream_response(stream_response_obj, sources),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return JSONResponse(
            content={
                "answer": "Sorry, there was an error processing your query. Please try again later.",
                "sources": []
            },
            status_code=500
        )

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
