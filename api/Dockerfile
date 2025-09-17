# Use official Python 3.12 image
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY dataq.pkl .
# Copy models
COPY insider_threat_model.pkl .


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
