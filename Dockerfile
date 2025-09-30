# Use a lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system deps (needed for PyPDF2, nltk, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (punkt + punkt_tab)
RUN python -m nltk.downloader punkt punkt_tab

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
