FROM python:3.10.18

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*


# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip + setuptools + wheel (important for numpy/pandas builds)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install numpy first
RUN pip install --no-cache-dir numpy==1.26.4

RUN apt-get update && apt-get install -y \
    gfortran \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements
COPY web_application/Backend/DataServer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy dataset processing code
COPY python_code/calculate_coefficients.py .
COPY web_application/Backend/FlaskApp/stats.py .
COPY web_application/Backend/DataServer/server.py .

# Create dirs
RUN mkdir -p /app/data /app/results /app/logs

# Permissions
RUN useradd -m -u 1000 processor && chown -R processor:processor /app
USER processor

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/health || exit 1

CMD ["python", "server.py"]
