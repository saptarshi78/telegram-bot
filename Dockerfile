# Base Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (e.g., ffmpeg, curl)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Copy your requirements.txt first to use Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Run your script (change main.py to your actual entry point)
CMD ["python", "main.py"]
