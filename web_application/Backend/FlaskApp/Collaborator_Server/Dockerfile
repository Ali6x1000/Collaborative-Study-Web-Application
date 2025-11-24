FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs models

# Expose port
EXPOSE 5002

# Set environment variables
ENV FLASK_APP=gui_app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "gui_app.py"]
