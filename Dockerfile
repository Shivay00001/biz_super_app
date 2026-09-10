FROM python:3.9-slim
RUN apt-get update && apt-get install -y python3-tk x11-apps && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
ENV DISPLAY=:0
ENTRYPOINT ["python", "migrate_db.py"]
