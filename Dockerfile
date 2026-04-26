# HuggingFace Space Dockerfile for CivicMind
# Optimized for Gradio deployment

FROM python:3.11-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_hf.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY openenv.yaml .
COPY setup.py .

# Copy necessary folders
COPY environment/ ./environment/
COPY agents/ ./agents/
COPY core/ ./core/
COPY rewards/ ./rewards/
COPY apis/ ./apis/

# Expose Gradio port (HuggingFace uses 7860)
EXPOSE 7860

# Run Gradio app
CMD ["python", "app.py"]
