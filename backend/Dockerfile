FROM python:3.11-slim

# Create non-root user first with proper UID/GID for volume mounting
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} appgroup && \
    useradd -m -u ${UID} -g appgroup appuser

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all application code first (required for hatchling to detect package structure)
COPY --chown=appuser:appgroup . .

# Install Python dependencies (using CPU-only PyTorch for smaller image)
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -e ".[dev]"

# Set ownership of installed packages and app directory
RUN chown -R appuser:appgroup /app /usr/local/lib/python3.11/site-packages

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
