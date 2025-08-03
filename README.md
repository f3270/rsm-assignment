# RSM - RAG System with Langfuse

A comprehensive RAG (Retrieval-Augmented Generation) system composed of two main components:
- **Langfuse**: Open-source LLM engineering platform for tracing, evaluation, and prompt management
- **RAG Microservice**: FastAPI-based microservice for document ingestion and querying

## Architecture

### High-Level Structure
```
RSM/
├── langfuse/                    # Git submodule - Langfuse platform
│   ├── web/                     # Next.js 14 frontend/backend
│   ├── worker/                  # Express.js background processor
│   └── packages/shared/         # Shared database schema and utilities
├── rag_microservice/            # FastAPI RAG service
│   ├── src/
│   │   ├── main.py             # Main API endpoints
│   │   ├── ingest.py           # Document ingestion logic
│   │   └── query.py            # Query and retrieval logic
│   └── Dockerfile              # Container configuration
├── docker-compose.yml          # Main orchestration file
└── util/                       # Utility scripts
└── test/                       # Test scripts
```

### Technology Stack
- **Langfuse Platform**: Next.js 14, tRPC, PostgreSQL, ClickHouse, Redis
- **RAG Service**: FastAPI, Python 3.13, uvicorn, ChromaDB, OpenAI
- **Infrastructure**: Docker, PostgreSQL, ClickHouse, Redis, MinIO

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python >=3.13 (for local development)
- Node.js and pnpm (for Langfuse development)

## Environment Variables

### Required Environment Variables

Create a `.env` file in the project root or set these in your environment:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Langfuse Configuration (for RAG service observability)
LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key
LANGFUSE_SECRET_KEY=sk-lf-your_secret_key
```

### Docker Environment Variables

The `docker-compose.yml` file contains all necessary environment variables for the containerized setup. Key variables include:

- `CHROMA_DB_DIR`: Vector database storage directory
- `LANGFUSE_HOST`: Internal service communication
- Database connection strings for PostgreSQL, ClickHouse, and Redis

## Building and Running

### Option 1: Full System (Recommended)

Build and start all services including Langfuse and RAG microservice:

```bash
# Build and start all services
./docker-compose-build-run.sh

# Alternative command
docker compose up --build
```

## Service Endpoints

### RAG Microservice (Port 8000)

- **Health Check**: `GET /health`
- **Document Ingestion**: `POST /ingest`
- **Document Query**: `POST /query`
- **API Documentation**: `GET /docs`

#### Ingest Endpoint

**URL**: `POST /ingest`

**Request Body**:
```json
{
  "source_type": "url" | "text",
  "content": "https://example.com/document.pdf" | "text content",
  "document_type": "pdf" | "text" | "html" | "markdown"
}
```

**Response**:
```json
{
  "status": "success" | "duplicate" | "error",
  "message": "Document ingested successfully",
  "chunks_created": 5
}
```

#### Query Endpoint

**URL**: `POST /query`

**Request Body**:
```json
{
  "question": "What is the main topic discussed in the documents?"
}
```

**Response**:
```json
{
  "answer": "The main topic is...",
  "sources": [
    {
      "page": 1,
      "text": "Relevant passage from the document..."
    }
  ]
}
```

### Langfuse Platform (Port 3000)

- **Main Web Interface**: `http://localhost:3000`
- **Development Login**: 
  - Email: `demo@langfuse.com`
  - Password: `password`

### Supporting Services

- **PostgreSQL**: Port 5432 (localhost only)
- **ClickHouse**: Port 8123 (localhost only)  
- **Redis**: Port 6379 (localhost only)
- **MinIO**: Port 9090 (S3-compatible storage)

## Testing

### Testing Document Ingestion

```bash
# Test URL ingestion
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "url",
    "content": "https://example.com/document.pdf",
    "document_type": "pdf"
  }'

# Test text ingestion
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "text", 
    "content": "This is a sample document for testing.",
    "document_type": "text"
  }'
```

### Testing Document Query

```bash
# Test query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What information is available in the documents?"
  }'
```

### Using Test Scripts

The project includes ready-to-use test scripts in the `test/` directory:

```bash
# Test text ingestion
./test/test_ingest_text_text.sh

# Test PDF ingestion from URL
./test/test_ingest_url_pdf.sh

# Test query functionality
./test/test_query_llm_langs.sh

# Make scripts executable if needed
chmod +x test/*.sh

# Run all tests in sequence
./test/test_ingest_text_text.sh && \
./test/test_ingest_url_pdf.sh && \
./test/test_query_llm_langs.sh
```

**Test Script Details:**
- `test_ingest_text_text.sh`: Ingests sample text about Langchain framework
- `test_ingest_url_pdf.sh`: Downloads and ingests a PDF from ArXiv (academic paper)
- `test_query_llm_langs.sh`: Queries about LLM response quality in different languages

## Features

### Document Processing
- **Supported Formats**: PDF, Text, HTML, Markdown
- **Source Types**: URL download, direct text input
- **Deduplication**: Automatic duplicate detection using content hashing
- **Metadata Tracking**: Source, document type, page numbers, ingestion timestamp

### Vector Storage
- **Database**: ChromaDB with persistent storage
- **Embeddings**: OpenAI embeddings
- **Persistence**: Docker volume mounted at `/app/vector_store`
- **Chunking**: Recursive text splitting (500 chars, 100 overlap)

### Query & Retrieval
- **Search**: Semantic similarity search
- **LLM**: OpenAI GPT-3.5-turbo for answer generation
- **Context**: Top 5 most relevant document chunks
- **Response Format**: Answer with source citations and page numbers

### Observability
- **Platform**: Langfuse integration
- **Tracing**: `@observe` decorators on key functions
- **Monitoring**: Request/response tracking, performance metrics

## Maintenance Commands

### Cleanup

```bash
# Clean all Docker resources
./docker-compose-clean-all.sh

# Remove temporary files
./util/clean.sh

# Clean specific services
docker compose down
docker volume prune
docker system prune
```

### Development

```bash
# View logs
docker compose logs rag-api
docker compose logs langfuse-web

# Restart specific service
docker compose restart rag-api

# Access service shell
docker compose exec rag-api /bin/bash
```

### Database Management

```bash
# Access PostgreSQL
docker compose exec langfuse-db psql -U langfuse -d langfuse

# Access ClickHouse
docker compose exec langfuse-clickhouse clickhouse-client

# View Redis data
docker compose exec langfuse-redis redis-cli
```

## Development Notes

- **RAG Service**: Uses `uv` for Python package management for development and pip for building app.
- **Langfuse**: Uses pnpm for Node.js dependencies  
- **Hot Reload**: Available in development mode for both services
- **Environment**: Default credentials provided for development (change for production)
- **Observability**: All key functions traced with Langfuse SDK v3

## Production Considerations

- Change all default passwords marked with `# CHANGEME`
- Use proper SSL certificates
- Configure proper backup strategies for databases
- Set up monitoring and alerting
- Use environment-specific configuration files
- Implement proper logging and error handling
