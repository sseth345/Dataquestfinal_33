# Use official Python 3.10 image (XGBoost compatible)
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy files
COPY requirements.txt .
COPY main.py .
COPY dataq.pkl .
COPY insider_threat_model.pkl .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
