FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY . .

COPY .env .env

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
