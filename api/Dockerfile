# Use Python 3.11 slim (xgboost compatible)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY ./app /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (match uvicorn port)
EXPOSE 10000

# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
