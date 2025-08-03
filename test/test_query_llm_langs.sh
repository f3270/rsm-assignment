#!/bin/bash

# URL base del servicio FastAPI
BASE_URL="http://localhost:8000"

# Pregunta a enviar al endpoint
QUESTION="¿Por qué varía la calidad de respuestas de los LLM en distintos lenguajes?"

# Solicitud POST al endpoint /query
curl -X POST "${BASE_URL}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "'"$QUESTION"'"
  }'

exit 0
