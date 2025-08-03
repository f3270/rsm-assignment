import datetime
import hashlib
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


def generate_content_hash(content: str, doc_type: str) -> str:
    """Generate consistent hash for deduplication"""
    # Normalize content (remove extra whitespace, lowercase for text types)
    if doc_type in ["text", "html", "markdown"]:
        normalized = ' '.join(content.strip().lower().split())
    else:
        normalized = content.strip()
    
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]  # 16 chars for brevity


def check_for_duplicates(content_hash: str, persist_dir: str) -> bool:
    """Check if document with this hash already exists"""
    try:
        # Load existing Chroma DB
        embeddings = OpenAIEmbeddings()
        db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        
        # Search for existing document with this hash
        results = db.get(where={"content_hash": content_hash})
        
        return len(results['documents']) > 0
    except Exception:
        # If DB doesn't exist yet or error, assume no duplicates
        return False


def _determine_page_for_chunk(chunk_text: str, page_info: list) -> int:
    """Determine which page a chunk belongs to based on text overlap"""
    if not page_info:
        return 1
    
    # Find the page with the most overlap with this chunk
    best_page = 1
    max_overlap = 0
    
    for page_num, page_text in page_info:
        # Simple overlap calculation - count common words
        chunk_words = set(chunk_text.lower().split())
        page_words = set(page_text.lower().split())
        overlap = len(chunk_words.intersection(page_words))
        
        if overlap > max_overlap:
            max_overlap = overlap
            best_page = page_num
    
    return best_page


@observe()
async def process_url(url: str, doc_type: str, source_id: str = None) -> tuple[str, int]:
    """Download and process content from URL"""
    response = httpx.get(url)
    response.raise_for_status()

    if doc_type == "pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()
            doc = fitz.open(temp_file.name)
            # Extract content with page information
            pages_content = []
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                if page_text.strip():  # Only include non-empty pages
                    pages_content.append((page_num, page_text))
            content = "\n".join([text for _, text in pages_content])
            # Store page information for later use
            page_info = pages_content
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

    # Generate content hash for deduplication
    content_hash = generate_content_hash(content, doc_type)
    persist_dir = os.getenv("CHROMA_DB_DIR", "./vector_store")
    
    # Check for duplicates before processing
    if check_for_duplicates(content_hash, persist_dir):
        return content, 0  # Return 0 chunks to indicate duplicate
    
    # Generate source_id if not provided
    if source_id is None:
        source_id = url
    
    # Prepare metadata for vectorization
    metadata = {"source": source_id, "content_hash": content_hash}
    
    # Pass page information if available (for PDFs)
    page_info = locals().get('page_info', None)
    chunks_created = vectorize_text(content, doc_type, metadata, page_info)

    return content, chunks_created


@observe()
def process_text(content: str, doc_type: str, source_id: str = None) -> tuple[str, int]:
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

    # Generate content hash for deduplication
    content_hash = generate_content_hash(processed_content, doc_type)
    persist_dir = os.getenv("CHROMA_DB_DIR", "./vector_store")
    
    # Check for duplicates before processing
    if check_for_duplicates(content_hash, persist_dir):
        return processed_content, 0  # Return 0 chunks to indicate duplicate
    
    # Generate source_id if not provided
    if source_id is None:
        source_id = f"text_{content_hash[:10]}"  # Use part of hash for source_id
    
    # Prepare metadata for vectorization
    metadata = {"source": source_id, "content_hash": content_hash}
    
    # For text input, we don't have page info, so pass None
    chunks_created = vectorize_text(processed_content, doc_type, metadata, None)

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
def vectorize_text(content: str, doc_type: str, metadata: dict = None, page_info: list = None) -> int:
    """Receives text and process it into vector DB"""
    raw_text = convert_text(content, doc_type)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_text(raw_text)
    
    # Prepare metadata for chunks
    if metadata is None:
        metadata = {}
    
    # Create individual metadata for each chunk
    metadatas = []
    for i, chunk_text in enumerate(chunks):
        # Determine page number for this chunk
        page_num = _determine_page_for_chunk(chunk_text, page_info) if page_info else 1
        
        chunk_metadata = {
            "source": metadata.get("source", "unknown"),
            "doc_type": doc_type,
            "ingested_at": datetime.datetime.now().isoformat(),
            "page": page_num,
            "text": chunk_text,  # Store chunk text for query responses
            "chunk_index": i,
            **metadata  # Include any additional metadata
        }
        metadatas.append(chunk_metadata)
    
    # Setup persistent directory
    persist_dir = os.getenv("CHROMA_DB_DIR", "./vector_store")
    
    # Create embeddings and store in persistent Chroma DB
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_texts(
        chunks, 
        embedding=embeddings, 
        metadatas=metadatas,
        persist_directory=persist_dir
    )
    
    # Data is automatically persisted with persist_directory in ChromaDB >= 0.4.x
    
    return len(chunks)
