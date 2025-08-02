from typing import List, Literal, Union

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl

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


async def process_url(url: str, document_type: str) -> tuple[str, int]:
    """Download and process content from URL"""
    # TODO: Implement URL downloading and processing
    # For now, return placeholder
    return f"Processed content from {url}", 1


async def process_text(content: str, document_type: str) -> tuple[str, int]:
    """Process text content directly"""
    # TODO: Implement text processing (chunking, embeddings)
    # For now, return placeholder
    chunks_created = len(content.split("\n\n"))  # Simple paragraph-based chunking
    return content, chunks_created


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """Ingest documents from URL or direct text"""
    try:
        if request.source_type == "url":
            processed_content, chunks_created = await process_url(
                str(request.content), request.document_type
            )
        elif request.source_type == "text":
            processed_content, chunks_created = await process_text(
                request.content, request.document_type
            )
        else:
            raise ValueError(f"Unsupported source_type: {request.source_type}")

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
