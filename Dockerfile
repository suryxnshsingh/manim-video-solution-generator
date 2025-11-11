FROM python:3.11-slim

# Install system dependencies for Manim and FFmpeg
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    python3-dev \
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-science \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directories
RUN mkdir -p output/solutions output/manim_code output/scripts output/videos output/audio output/final

# Set environment variable for Manim
ENV MANIMGL_CACHE_DIR=/tmp/manim_cache

CMD ["python", "main.py"]
