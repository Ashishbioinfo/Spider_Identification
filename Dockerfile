# Use Python 3.12 slim image (better support for TensorFlow)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python train_model_fixed.py

# Copy application files
COPY api.py .
COPY setup_model.py .
COPY frontend/ ./frontend/

# Create required directories (dataset/model may be uploaded separately or generated)
RUN mkdir -p uploads model dataset/spider_images

# Expose port
EXPOSE 5000

# Set environment variable
ENV FLASK_APP=api.py

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:app"]
