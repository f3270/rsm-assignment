# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) microservice built with FastAPI and Python. The project uses `uv` as the package manager and includes Docker containerization for deployment.

## Development Commands

### Local Development
- **Run development server**: `./run_fastapi.sh` or `uv run fastapi dev src/main.py`
- **Install dependencies**: `uv sync` (uv handles dependencies via pyproject.toml)

### Docker Development
- **Build Docker image**: `./docker_build.sh` or `docker build -t rag_microservice .`
- **Run Docker container**: `./docker_run.sh` or `docker run -p 8000:8000 rag_microservice`

## Architecture

### Project Structure
- `src/main.py`: Main FastAPI application entry point with basic routes
- `pyproject.toml`: Python project configuration with FastAPI and uvicorn dependencies
- `requirements.txt`: Legacy requirements file (project uses uv for dependency management)
- Docker configuration for containerized deployment

### Technology Stack
- **Web Framework**: FastAPI with uvicorn server
- **Package Management**: uv (modern Python package manager)
- **Python Version**: Requires Python >=3.13 (development), uses Python 3.11 in Docker
- **Containerization**: Docker with Python 3.11-slim base image

### API Endpoints
- `GET /`: Returns basic "Hello World" response
- `GET /items/{item_id}`: Example parameterized endpoint with optional query parameter

## Development Notes

- The project is configured to run on port 8000
- FastAPI development mode includes hot-reload functionality
- Docker container exposes port 8000 and runs with uvicorn in production mode
- The codebase follows standard FastAPI patterns with type hints using `typing.Union`