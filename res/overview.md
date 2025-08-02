# RAG MICROSERVICE

+ Fast-API
    + [x] endpoints
    + [x] schemas
    + local  -> http://127.0.0.1:8000
    + docker -> http://0.0.0.0:8000/docs

+ Docker
    + [x] build
    + [x] run

+ Langfuse
    + [x] http://0.0.0.0:3000/auth/sign-in

+ [x] Docker-Compose

+ Ingest
    + [ ] filetypes: pdf | text | html | markdown
    + [ ] chunks
    + [ ] embeddings
    + [ ] vector db

+ LLM Query

---

```mermaid
graph TD
    subgraph RAG Microservice
        FastAPI["FastAPI API"]
        Ingest["/ingest Endpoint"]
        Query["/query Endpoint"]
        Health["/health Endpoint"]
        Langfuse["Langfuse Observability"]
    end

    subgraph Storage Layer
        Chroma["ChromaDB (Vector Store)"]
    end

    subgraph External Services
        OpenAI["OpenAI LLM API"]
        Documents["External Documents (ThinkPython, PEP8)"]
    end

    %% Connections
    Documents -->|Load & Chunk| Ingest
    Ingest -->|Store embeddings| Chroma
    Query -->|Retrieve embeddings| Chroma
    Query -->|Generate Answer| OpenAI
    FastAPI -->|Instrument Spans, Metrics| Langfuse
    FastAPI --> Health

    %% User interaction
    User["User/API Client"] -->|HTTP Requests| FastAPI
```
