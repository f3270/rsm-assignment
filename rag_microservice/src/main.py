import uuid
from typing import List, Literal, Union

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

from ingest import process_text, process_url

app = FastAPI()


class IngestFromURL(BaseModel):
    source_type: Literal["url"]
    content: HttpUrl
    document_type: Literal["pdf", "text", "html", "markdown"]


class IngestFromText(BaseModel):
    source_type: Literal["text"]
    content: str
    document_type: Literal["pdf", "text", "html", "markdown"]


IngestRequest = Union[IngestFromURL, IngestFromText]


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
async def ingest_document(request: IngestRequest):
    """Ingest documents from URL or direct text"""
    try:
        if request.source_type == "url":
            source_id = f"url_{str(request.content)}"
            processed_content, chunks_created = await process_url(
                str(request.content), request.document_type, source_id
            )
        elif request.source_type == "text":
            source_id = f"text_{str(uuid.uuid4())[:8]}"
            processed_content, chunks_created = process_text(
                request.content, request.document_type, source_id
            )
        else:
            raise ValueError(f"Unsupported source_type: {request.source_type}")

        if chunks_created == 0:
            return IngestResponse(
                status="duplicate",
                message="Document already exists (duplicate detected)",
                chunks_created=0,
            )
        else:
            return IngestResponse(
                status="success",
                message="Document ingested successfully",
                chunks_created=chunks_created,
            )
    except Exception as e:
        return IngestResponse(
            status="error",
            message=f"Failed to ingest document: {str(e)}",
            chunks_created=0,
        )


@app.post("/query", response_model=QueryResponse)
def query_documents(request: QueryRequest):
    # TODO: Implement query logic
    return QueryResponse(answer="This is a placeholder answer", sources=[])
