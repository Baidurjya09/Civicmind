# CivicMind — Production Docker Image
# Build: docker build -t civicmind:latest .
# Run:   docker run --gpus all -v $(pwd)/training:/app/training civicmind:latest

FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create necessary directories
RUN mkdir -p training/checkpoints evaluation logs

# Expose ports
EXPOSE 8080 8501

# Default command (can be overridden)
CMD ["python", "evaluate.py", "--mode", "compare"]
