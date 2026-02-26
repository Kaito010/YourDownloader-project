FROM python:3.11-slim

# Instala FFmpeg e Node.js para o yt-dlp funcionar sem bloqueios
RUN apt-get update && apt-get install -y ffmpeg nodejs && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tudo, inclusive seu cookies.txt
COPY . .

# Comando que o Docker vai usar para ligar o site
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]