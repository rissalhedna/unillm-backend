# uniLLM Backend

A FastAPI-based backend service for the German Student Info Chatbot, providing RAG (Retrieval-Augmented Generation) capabilities with vector search and LLM integration.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [API Endpoints](#api-endpoints)
- [Data Pipeline](#data-pipeline)
- [Deployment](#deployment)

## Overview

The uniLLM backend is built with:

- **FastAPI** - Modern, fast web framework for building APIs
- **LlamaIndex** - RAG framework for document indexing and retrieval
- **Qdrant** - Vector database for semantic search
- **OpenAI GPT-4** - Large language model for response generation

## Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

## Installation

1. Clone the repository:

```bash
git clone https://github.com/rissalhedna/unillm.git
cd unillm-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the required services:

```bash
docker compose up -d
```

This will start:

- PostgreSQL database on port 5432
- Qdrant vector database on port 6333

## Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres

# Qdrant Vector Database
QDRANT_HOST=127.0.0.1
QDRANT_PORT=6333
QDRANT_URL=http://127.0.0.1:6333

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Environment
DEV=dev  # or "prod" for production
```

## Development

### Local Development

1. Start the development server:

```bash
fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`

2. Access the interactive API documentation:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

### Docker Development

1. Build and run with Docker:

```bash
docker compose up --build
```

### Code Quality

Before committing changes, run pre-commit hooks:

```bash
pre-commit run --all-files
```

## API Endpoints

### Chat Endpoints

- `POST /chat` - Send a message to the chatbot
- `GET /chats` - Retrieve chat history
- `GET /chats/{chat_id}` - Get specific chat conversation

### Health Check

- `GET /health` - API health status

### Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Data Pipeline

The backend includes a comprehensive data processing pipeline for managing the knowledge base:

### Web Scraping

Located in `/scripts` folder:

- `handbook_germany_crawler.py` - Scrapes handbook-germany.de
- `study_in_germany_crawler.py` - Scrapes study-in-germany.de

### Data Processing

The pipeline processes data through:

1. **Web Scraping**: Automated crawlers collect information from German study websites
2. **Data Cleaning**: Raw data is processed and cleaned
3. **Text Chunking**: Documents are split into appropriate chunks for embeddings
4. **Vectorization**: Text chunks are converted to embeddings using OpenAI
5. **Storage**: Embeddings are stored in Qdrant vector database

### Running the Pipeline

1. Install browser dependencies:

```bash
playwright install chromium
```

2. Run scrapers:

```bash
cd scripts
python handbook_germany_crawler.py
python study_in_germany_crawler.py
```

3. Process the data using the notebook:

```bash
jupyter notebook notebooks/scraping_cleaning_pipeline.ipynb
```

## Architecture

```
User Query → FastAPI → LlamaIndex → Qdrant (Vector Search) → OpenAI GPT-4 → Response
```

### Key Components

- **Query Processing**: FastAPI receives and validates user queries
- **RAG System**: LlamaIndex orchestrates retrieval and generation
- **Vector Search**: Qdrant finds relevant document chunks
- **Response Generation**: OpenAI GPT-4 generates contextual responses
- **Fallback System**: Search engine fallback for queries outside knowledge base

## Deployment

### Production Deployment

1. Set environment variables for production
2. Use Docker for containerized deployment:

```bash
docker build -t unillm-backend .
docker run -p 8000:8000 unillm-backend
```

### Deployment Platforms

- **Railway**: Simple deployment with database support
- **Linode**: Cost-effective VPS hosting
- **Docker**: Containerized deployment

## Current Status

✅ Working Features:

- FastAPI backend with async support
- RAG system with Qdrant integration
- Document indexing and retrieval
- OpenAI GPT-4 integration
- Web scraping pipeline
- Docker containerization

🔧 Known Issues:

- Chat history persistence needs improvement
- Search engine fallback system in development

🚧 Upcoming Features:

- Enhanced search engine fallback
- CV matching functionality
- Improved caching system
- Rate limiting and authentication
- Monitoring and logging improvements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and pre-commit hooks
5. Submit a pull request

## License

This project is licensed under the MIT License.
