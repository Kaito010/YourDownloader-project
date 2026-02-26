FROM python:3.11-slim

# Instala FFmpeg e Node.js (essencial para burlar o JS runtime)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]