from typing import List, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class IngestRequest(BaseModel):
    content: str
    document_type: str


class IngestResponse(BaseModel):
    status: str
    message: str
    chunks_created: int


class QueryRequest(BaseModel):
    question: str


class Source(BaseModel):
    page: int
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]


@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.post("/ingest", response_model=IngestResponse)
def ingest_document(request: IngestRequest):
    # TODO: Implement document ingestion logic
    return IngestResponse(
        status="success", message="Document ingested successfully", chunks_created=0
    )


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    # TODO: Implement query logic
    return QueryResponse(answer="This is a placeholder answer", sources=[])
