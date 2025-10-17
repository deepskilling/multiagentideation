# Multi-Agent Ideation System - Docker Image
# Base: Python 3.10 slim
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY core/ ./core/
COPY config.py .
COPY main.py .
COPY deep_ideation.py .
COPY prd_generator.py .
COPY event_ideator.py .

# Create necessary directories
RUN mkdir -p data reports logs

# Copy documentation (optional, for reference)
COPY docs/ ./docs/
COPY COMMAND_REFERENCE.md .
COPY README.md .

# Set permissions
RUN chmod +x main.py deep_ideation.py prd_generator.py event_ideator.py

# Health check endpoint (optional - for API mode)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command: run main.py generate with sample prompt
CMD ["python", "main.py", "generate", "--prompt", "Sample SaaS idea", "--num-ideas", "3"]

# For interactive use:
# docker run -it <image> /bin/bash

# For custom commands:
# docker run <image> python deep_ideation.py "YOUR DOMAIN" --num-ideas 10

