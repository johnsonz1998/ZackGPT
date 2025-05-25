# ZackGPT Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libportaudio2 \
    build-essential \
    git \
    python3.10-dev \
    libpython3.10-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN echo '🔍 Installing Python requirements:' && \
    cat requirements.txt && \
    pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/     ./app/
COPY voice/   ./voice/
COPY llm/     ./llm/
COPY scripts/ ./scripts/

# Default startup command
CMD ["python", "scripts/startup/main.py"]
