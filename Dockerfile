# Usa uma imagem leve do Python
FROM python:3.10-slim

# Instala o FFmpeg dentro do container Linux
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Define a pasta de trabalho dentro do servidor
WORKDIR /app

# Copia os arquivos de configuração primeiro (otimiza o cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do seu código
COPY . .

# Expõe a porta
EXPOSE 5000

# Comando para iniciar o site
CMD ["python", "app.py"]