# Dockerfile for CAD Educational Assessment System
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for mesh processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY setup.py .
COPY README.md .
COPY LICENSE .

# Create necessary directories
RUN mkdir -p sample_models/teacher \
    sample_models/students \
    reports \
    .streamlit

# Create Streamlit config
RUN echo '[theme]\n\
primaryColor = "#667eea"\n\
backgroundColor = "#ffffff"\n\
secondaryBackgroundColor = "#f0f2f6"\n\
textColor = "#262730"\n\
font = "sans serif"\n\
\n\
[server]\n\
maxUploadSize = 200\n\
enableCORS = false\n\
enableXsrfProtection = true\n\
port = 8501\n\
address = "0.0.0.0"\n\
\n\
[browser]\n\
gatherUsageStats = false' > .streamlit/config.toml

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ===== docker-compose.yml =====
version: '3.8'

services:
  cad-assessment:
    build: .
    container_name: cad-assessment-system
    ports:
      - "8501:8501"
    volumes:
      - ./sample_models:/app/sample_models
      - ./reports:/app/reports
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_SERVER_PORT=8501
    restart: unless-stopped
    networks:
      - cad-network

networks:
  cad-network:
    driver: bridge

# ===== .dockerignore =====
venv/
env/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.git/
.gitignore
.streamlit/secrets.toml
reports/*.md
reports/*.pdf
reports/*.zip
*.step
*.stp
*.iges
*.igs
.DS_Store
Thumbs.db
*.swp
