# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) system composed of two main components:
- **Langfuse**: Open-source LLM engineering platform for tracing, evaluation, and prompt management (git submodule)
- **RAG Microservice**: FastAPI-based microservice for document ingestion and querying

The project uses Docker Compose to orchestrate multiple services including PostgreSQL, ClickHouse, Redis, MinIO, and the custom RAG API.

## Architecture

### High-Level Structure
```
RSM/
├── langfuse/                    # Git submodule - Langfuse platform
│   ├── web/                     # Next.js 14 frontend/backend
│   ├── worker/                  # Express.js background processor
│   └── packages/shared/         # Shared database schema and utilities
├── rag_microservice/            # FastAPI RAG service
│   ├── src/main.py             # Main API endpoints
│   └── Dockerfile              # Container configuration
├── docker-compose.yml          # Main orchestration file
└── util/                       # Utility scripts
```

### Technology Stack
- **Langfuse Platform**: Next.js 14, tRPC, PostgreSQL, ClickHouse, Redis
- **RAG Service**: FastAPI, Python 3.13, uvicorn
- **Infrastructure**: Docker, PostgreSQL, ClickHouse, Redis, MinIO

## Development Commands

### Full System Startup
```bash
./docker-compose-build-run.sh    # Build and start all services
docker compose up --build        # Alternative command
```

### Individual Service Development
```bash
# RAG Microservice only
cd rag_microservice/
./run_fastapi.sh                 # Local development server
./docker_build.sh               # Build Docker image
./docker_run.sh                 # Run containerized version

# Langfuse only (see langfuse/CLAUDE.md for detailed commands)
cd langfuse/
pnpm run dev:web                 # Web app only (port 3000)
pnpm run infra:dev:up           # Start dependencies
```

### Utility Commands
```bash
./docker-compose-clean-all.sh    # Clean all Docker resources
./util/clean.sh                  # Remove temporary files
```

## Service Endpoints

### RAG Microservice (Port 8000)
- `GET /health` - Health check
- `POST /ingest` - Document ingestion (placeholder)
- `POST /query` - Document querying (placeholder)
- `GET /docs` - FastAPI documentation

### Langfuse Platform (Port 3000)
- Main web interface for LLM observability
- Development login: `demo@langfuse.com` / `password`

### Supporting Services
- **PostgreSQL**: Port 5432 (localhost only)
- **ClickHouse**: Port 8123 (localhost only)
- **Redis**: Port 6379 (localhost only)
- **MinIO**: Port 9090 (S3-compatible storage)

## Environment Configuration

The system uses environment variables defined in `docker-compose.yml`. Key configurations:
- Database URLs and credentials
- API keys for OpenAI and Langfuse integration
- S3/MinIO storage settings
- Redis configuration

**Note**: Default credentials are provided for development but should be changed for production (marked with `# CHANGEME`).

## Development Notes

### RAG Service Development
- Uses `uv` for Python package management
- Requires Python >=3.13 for local development
- FastAPI with type hints and Pydantic models
- Current implementation has placeholder endpoints for ingest/query functionality

### Langfuse Integration
- The RAG service is configured to send observability data to Langfuse
- Langfuse runs as a separate service with its own database
- Both services share the same Docker network for communication

### Docker Development
- All services are containerized and orchestrated via Docker Compose
- The RAG service builds from a Python 3.11-slim base image
- Langfuse uses pre-built images from Docker Hub
- Volumes are used for data persistence across container restarts

## Observability Notes
- To implement observability with Langfuse, use the following documentation:
  + https://langfuse.com/docs/observability/sdk/python/sdk-v3
  + According to the official site, use the `@observe` decorator for tracing

## Langfuse Configuration Details
- Langfuse requires both client initialization and environment configuration
- Steps for Langfuse setup:
  + Set environment variables for Langfuse credentials
    ```python
    import os

    os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
    os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
    os.environ["LANGFUSE_HOST"] = "http://localhost:3000"
    ```
  + Use `@observe` decorator for function tracing
    ```python
    from langfuse.decorators import observe

    @observe()
    def vectorize_text(content: str, doc_type: str) -> int:
        # function implementation
        pass
    ```
  + In short-lived environments, call `flush()` to ensure event collection
    ```python
    from langfuse.decorators import langfuse_context

    langfuse_context.flush()
    ```

## Memory Notes
- Remember that in Langfuse we are using SDK v3