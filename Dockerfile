# CodePulse AI - Production Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements-dev.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-dev.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 codepulse && \
    chown -R codepulse:codepulse /app

USER codepulse

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/v1/phase6/health || exit 1

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0"]
