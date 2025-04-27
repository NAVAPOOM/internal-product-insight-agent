FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create directories and set permissions
RUN mkdir -p /app/documents /app/chroma_db /app/logs \
    && chown -R appuser:appuser /app

# Copy application code
COPY . .

# Set ownership for all files
RUN chown -R appuser:appuser /app

# Switch to non-root user
# USER appuser

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCUMENTS_DIR=/app/documents \
    VECTOR_STORE_DIR=/app/chroma_db \
    LOG_FILE=/app/logs/app.log

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Define volumes for persistent data
VOLUME ["/app/documents", "/app/chroma_db"]

# Command to run the application
ENTRYPOINT ["python"]
CMD ["main.py"]