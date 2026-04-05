FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (create it first if it doesn't exist)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose port
ENV PORT=10000
EXPOSE 10000

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
