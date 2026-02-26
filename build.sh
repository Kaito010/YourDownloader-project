#!/usr/bin/env bash
# Sair se houver erro
set -o errexit

# Instalar dependências de Python
pip install -r requirements.txt

# Instalar um runtime de JS (Node.js) e FFmpeg para o Render
# Isso resolve o aviso "No supported JavaScript runtime"
apt-get update && apt-get install -y nodejs ffmpeg