# uniLLM: Project plan

# German Student Info Chatbot

A chatbot application to provide information for students in Germany, built with FastAPI, Svelte, and LlamaIndex.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Development](#development)

## Prerequisites

- Python 3.8+
- Node.js and npm
- Git
- Docker (optional, for containerized backend)

## Installation

### Option 1: Local Installation

1. Clone the repository:

```bash
git clone https://github.com/rissalhedna/unillm.git
cd unillm
```

2. Set up backend:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
pip install pre-commit
pre-commit install
```

3. Set up frontend:

```bash
cd frontend
npm install
```

### Option 2: Docker Backend

1. Clone the repository:

```bash
git clone https://github.com/rissalhedna/unillm.git
cd unillm
```

2. Build and start the backend container:

```bash
docker compose build
docker compose up -d  # The backend will run on localhost:8000
```

3. Set up frontend:

```bash
cd frontend
npm install
```

## Development

### Option 1: Local Development

1. Start the backend server:

```bash
cd ..
fastapi dev main.py  # The app runs on localhost:8000
```

2. In a new terminal, start the frontend:

```bash
cd frontend
npm run dev  # The frontend runs on localhost:3000
```

3. Access the application at `http://localhost:3000`.

4. Before committing changes, run pre-commit hooks:

```bash
pre-commit run --all-files
```

### Option 2: Docker Development

1. Start the backend using Docker:

```bash
docker compose up -d  # The backend runs on localhost:8000
```

2. In a new terminal, start the frontend:

```bash
cd frontend
npm run dev  # The frontend runs on localhost:3000
```

3. Access the application at `http://localhost:3000`.

## Data Pipeline

The data processing pipeline consists of two main components:

1. Web scraping using Scrapy (located in `/scripts` folder)
2. Data processing and vectorization (located in `/notebooks/scraping_cleaning_pipeline.ipynb`)

To add new data to the system:

1. Ensure environment variables are set up in `.env`:

```
QDRANT_HOST=your_qdrant_host
QDRANT_PORT=your_qdrant_port
OPENAI_API_KEY=your_openai_key  # For embedding generation
DEV=["prod", "dev"]
```

2. Install required browser for web scraping:

```bash
playwright install  # Installs all supported browsers
# Or for a specific browser:
playwright install chromium
```

3. Run the Scrapy scrapers from the scripts folder:

```bash
cd scripts
scrapy runspider [scraper_file]
```

This will generate JSON files with the raw scraped data.

4. Process the data using the notebook:

- Open `/notebooks/scraping_cleaning_pipeline.ipynb`
- This notebook contains all the logic to:
  - Clean and preprocess the scraped data
  - Chunk the text into appropriate sizes
  - Generate embeddings
  - Save the data into Qdrant vector database

Make sure to run the notebook cells in order and verify that all environment variables are properly set before processing the data.

## Current Status

The chatbot is currently in active development with the following status:

✅ Working Features:

- Basic chatbot functionality
- Integration with Qdrant database
- Information retrieval from study-in-germany website

🔧 Known Issues:

- Some bugs in the frontend

🚧 Upcoming Features:

- Search engine fallback system
- CV matching functionality
- Enhanced data processing pipeline
- Improved response accuracy
- Regular data updates

## Roadmap

### Current Phase: Phase 1 (In Progress)

### Phase 1: Core Chatbot Development

- ✅ Set up basic infrastructure
- ✅ Implement RAG system
- 🚧 Integrate search engine fallback
- 🚧 Develop basic frontend (similar to ChatGPT)

### Phase 2: Data Collection and Optimization

- Gather and process information about studying in Germany
- Optimize RAG system based on user feedback
- Recursively updating specific data (probably through a crawler - check perplexity crawler)
- Refine the dataset for better quality
- Improve the indexing and document encoding and retrieval

### Phase 3: CV Matching Feature (Bonus)

- Develop CV upload and processing functionality
- Implement university matching algorithm

### Phase 4: Testing and Refinement

- Conduct thorough testing
- Gather user feedback

### Phase 5: Deployment and Maintenance

- Deploy to production
- Set up basic monitoring

## Minimal Cost Tech Stack

### Frontend:

- Framework: Svelte
- Hosting: Netlify (free tier)

### Backend:

- Framework: FastAPI
- Hosting: Linode (minimal plan, ~$5/month)

### Vector Database:

- Qdrant (self-hosted on Linode instance)

### LLM:

- Open-source model: OpenAI gpt 4

### RAG Framework:

- LlamaIndex (open-source)

### Search Engine Fallback:

- SerpApi or Perplexica (100 free searches/month)

### Version Control and CI/CD:

- Git for version control
- GitHub Actions for CI/CD (free for public repositories)

### Document Processing (for CV feature):

- PyPDF2 for PDF parsing (open-source)
- spaCy for NLP tasks (open-source)

## Overview of the Application

### Core Chatbot System:

- User Interface: Svelte-based chat interface
- Query Processing: FastAPI backend receives user queries
- RAG System:
  - LlamaIndex processes the query
  - Qdrant performs vector similarity search
  - LLaMA 3 7B generates response based on retrieved context
- Search Engine Fallback:
  - Triggered when RAG system doesn't find relevant information
  - Uses SerpApi to fetch search results

### CV Matching Feature (Bonus):

- CV Upload: Allow users to upload CV in PDF format
- CV Processing:
  - Extract relevant information using PyPDF2 and spaCy
  - Generate embeddings for CV content
- University Matching:
  - Compare CV embeddings with university requirements/profiles
  - Rank universities based on similarity scores

### Data Management:

- Regular manual updates to the knowledge base about German universities and student life (for now)

### Monitoring and Improvement:

- Use basic logging and manual review of chat logs for improvements (Logger)
