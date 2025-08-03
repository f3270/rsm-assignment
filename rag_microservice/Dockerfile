FROM python:3.11-slim

# Instala dependencias del sistema (ajusta según tus libs: pdf, html, etc.)
RUN apt-get update && apt-get install -y 

# Crea el directorio de trabajo
WORKDIR /app
RUN mkdir -p /app/vector_store && chown -R 1000:1000 /app/vector_store

# Copia los archivos necesarios
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# Expone el puerto de FastAPI
EXPOSE 8000

# Agrega el directorio src al PYTHONPATH para que encuentre los módulos
ENV PYTHONPATH=/app/src

# Ejecuta la app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
