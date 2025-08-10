# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements (if you have one) and source code
COPY main.py ./
COPY scraper.py ./
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "main.py"]