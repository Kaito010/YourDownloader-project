FROM python:3.11-slim

# Instala FFmpeg e dependências iniciais
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instala o Node.js (necessário para resolver o 'n challenge' do YouTube)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código e os cookies
COPY . .

# Expõe a porta e inicia o Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]