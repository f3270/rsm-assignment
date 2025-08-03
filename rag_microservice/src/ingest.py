import os
import tempfile

import fitz
import httpx
import markdown
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langfuse import observe


@observe()
async def process_url(url: str, doc_type: str) -> tuple[str, int]:
    """Download and process content from URL"""
    response = httpx.get(url)
    response.raise_for_status()

    if doc_type == "pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()
            doc = fitz.open(temp_file.name)
            content = "\n".join([page.get_text() for page in doc])
            doc.close()
            os.unlink(temp_file.name)
    elif doc_type == "text":
        content = response.text
    elif doc_type == "html":
        content = BeautifulSoup(response.text, "html.parser").get_text()
    elif doc_type == "markdown":
        html = markdown.markdown(response.text)
        content = BeautifulSoup(html, "html.parser").get_text()
    else:
        raise ValueError("Unsupported document_type for URL input")

    chunks_created = vectorize_text(content, doc_type)

    return content, chunks_created


@observe()
def process_text(content: str, doc_type: str) -> tuple[str, int]:
    """Process text content directly"""
    if doc_type == "markdown":
        html = markdown.markdown(content)
        processed_content = BeautifulSoup(html, "html.parser").get_text()
    elif doc_type == "html":
        processed_content = BeautifulSoup(content, "html.parser").get_text()
    elif doc_type == "text":
        processed_content = content
    else:
        raise ValueError("Unsupported document_type for text input")

    chunks_created = vectorize_text(processed_content, doc_type)

    return processed_content, chunks_created


@observe()
def convert_text(content: str, doc_type: str) -> str:
    """Convert text based on document type"""
    if doc_type in ["text", "pdf"]:
        return content
    elif doc_type == "html":
        return BeautifulSoup(content, "html.parser").get_text()
    elif doc_type == "markdown":
        html = markdown.markdown(content)
        return BeautifulSoup(html, "html.parser").get_text()
    else:
        raise ValueError(f"Unsupported document_type: {doc_type}")


@observe()
def vectorize_text(content: str, doc_type: str) -> int:
    """Receives text and process it into vector DB"""
    raw_text = convert_text(content, doc_type)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(raw_text)
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_texts(chunks, embedding=embeddings)
    return len(chunks)
