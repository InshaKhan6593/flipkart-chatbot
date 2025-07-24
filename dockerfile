# Use a minimal Python 3.12 image
FROM python:3.12-slim

# Prevent Python from creating .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Copy all local project files to /app in container
COPY . .

# Install Python dependencies from requirements.txt (⚠️ Fix this line)
RUN pip install --no-cache-dir -e .

# Expose port 5000 for external access
EXPOSE 5000

# Run your app when container starts
CMD ["python", "app.py"]
