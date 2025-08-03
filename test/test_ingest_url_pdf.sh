#!/bin/bash

# Define variables
URL="http://localhost:8000/ingest"
SOURCE_TYPE="url"
CONTENT="https://arxiv.org/pdf/2305.07004"
DOC_TYPE="pdf"

# Ejecuta la solicitud
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"source_type\": \"$SOURCE_TYPE\",
    \"content\": \"$CONTENT\",
    \"document_type\": \"$DOC_TYPE\"
  }"

exit 0
