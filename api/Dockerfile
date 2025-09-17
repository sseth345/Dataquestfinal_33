# Use official Python image
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY main.py .
COPY dataq.pkl .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

COPY . /app
WORKDIR /app
