# Use a slim Python base
FROM python:3.11-slim

# Install system deps (ping) and make non-interactive
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /app

# Copy only requirements first to leverage docker cache
COPY requirements.txt /app/requirements.txt

# Install Python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Ensure proper permissions
RUN chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1
ENV UVICORN_CMD="uvicorn main:app --host 0.0.0.0 --port 8000"

EXPOSE 8000

CMD ["sh", "-c", "${UVICORN_CMD}"]
