# Start from a base image with Python
FROM python:3.12.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Redis (for Debian-based images)
RUN apt-get update && apt-get install -y redis-server

# Copy the rest of the application code to the container
COPY . .

# Set PYTHONPATH to include the current working directory
ENV PYTHONPATH=/app

# Set build arguments for the environment variables
ENV FASTAPI_URL=http://localhost:2345/suggestions

# Expose ports for FastAPI and Redis (if needed)
EXPOSE 2345
EXPOSE 6379

# Run tests using pytest
RUN service redis-server start && pytest tests/test.py

# Command to start Redis and run the FastAPI application
CMD ["sh", "-c", "service redis-server start && uvicorn autocomplete_service.server:app --host 0.0.0.0 --port 2345"]
