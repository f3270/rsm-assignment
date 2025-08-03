import os
from typing import List, Tuple

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langfuse import observe


@observe()
def query_vectordb(question: str) -> Tuple[str, List[dict]]:
    """
    Query the vector database and generate an answer using RAG
    
    Args:
        question: User's question to search for
        
    Returns:
        Tuple of (answer_string, sources_list)
        where sources_list contains dicts with 'page' and 'text' keys
    """
    # Get the persistent directory
    persist_dir = os.getenv("CHROMA_DB_DIR", "./vector_store")
    
    # Initialize embeddings and load the existing vector database
    embeddings = OpenAIEmbeddings()
    db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    
    # Perform similarity search to get relevant chunks
    # Get top 5 most relevant chunks with their scores
    relevant_docs = db.similarity_search_with_score(question, k=5)
    
    if not relevant_docs:
        return "I couldn't find any relevant information to answer your question.", []
    
    # Extract sources for the response
    sources = []
    context_texts = []
    
    for doc, score in relevant_docs:
        # Extract metadata from the document
        metadata = doc.metadata
        page_num = metadata.get('page', 1)
        text_content = metadata.get('text', doc.page_content)
        
        # Add to sources list (for response)
        sources.append({
            "page": page_num,
            "text": text_content
        })
        
        # Add to context for LLM (limit length to avoid token limits) 
        context_texts.append(f"Page {page_num}: {text_content[:500]}...")
    
    # Combine context for the LLM
    context = "\n\n".join(context_texts)
    
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Create the prompt for answer generation
    prompt = f"""Based on the following context, please answer the question. Be concise and accurate.

Context:
{context}

Question: {question}

Answer:"""
    
    # Generate the answer
    response = llm.invoke(prompt)
    answer = response.content.strip()
    
    return answer, sources