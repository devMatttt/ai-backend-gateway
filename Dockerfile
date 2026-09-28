# Use lightweight official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files, enable unbuffered output, and set PYTHONPATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace

WORKDIR /workspace

# Install system dependencies needed for health checks / curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code into container
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Start Uvicorn web server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]