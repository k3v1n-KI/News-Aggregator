# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set working directory
WORKDIR /app

# Install required build tools and headers
RUN apt-get update && \
    apt-get install -y gcc g++ make build-essential python3-dev libffi-dev libssl-dev curl ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first to leverage Docker caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose port 
EXPOSE 8080

# Start the app
CMD ["python", "main.py"]
