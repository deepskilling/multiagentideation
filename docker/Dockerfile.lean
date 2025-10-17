# Multi-Agent Ideation System - Lean Docker Image
# Target: <400MB (vs 2.8GB original)
# Optimized for AWS ECS/Fargate deployment

FROM python:3.10-slim AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Disable heavy optional features
    DISABLE_EMBEDDINGS=1

# Install only essential system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy minimal requirements
COPY docker/requirements.minimal.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip && \
    find /usr/local/lib/python3.10 -name '*.pyc' -delete && \
    find /usr/local/lib/python3.10 -name '__pycache__' -delete

# Copy application code (only what's needed for CLI)
COPY agents/ ./agents/
COPY core/ ./core/
COPY config.py .
COPY main.py .
COPY deep_ideation.py .
COPY prd_generator.py .

# Create necessary directories
RUN mkdir -p data reports logs

# Remove any remaining cache/temp files
RUN find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find . -type f -name '*.pyc' -delete 2>/dev/null || true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "main.py", "generate", "--prompt", "Sample SaaS idea", "--num-ideas", "3"]
