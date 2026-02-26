# Usa uma imagem oficial do Python
FROM python:3.11-slim

# Instala FFmpeg e Node.js (necessário para o yt-dlp não ser bloqueado)
RUN apt-get update && apt-get install -y ffmpeg nodejs && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código e os cookies
COPY . .

# Comando para iniciar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]