#!/bin/bash

# Define variables
URL="http://localhost:8000/ingest"
SOURCE_TYPE="text"
CONTENT="Langchain is a framework for building applications powered by language models. It provides tools for chaining LLMs with external data sources, memory, and user interactions."
DOC_TYPE="text"

# Ejecuta la solicitud
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"source_type\": \"$SOURCE_TYPE\",
    \"content\": \"$CONTENT\",
    \"document_type\": \"$DOC_TYPE\"
  }"

exit 0
