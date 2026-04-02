FROM python:3.11-slim

# Install system dependencies for psycopg2 and PDF processing
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# PRE-DOWNLOAD THE MODEL so the container starts instantly
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

COPY . .

# Use unbuffered output so logs appear immediately in Docker logs
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]