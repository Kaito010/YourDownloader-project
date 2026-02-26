from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import re

app = Flask(__name__)

# Configuração de caminhos absolutos para o Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Validação de Segurança
YOUTUBE_REGEX = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$"

# Opções base para evitar bloqueios (com Cookies e JS Runtime)
BASE_YDL_OPTS = {
    'quiet': True,
    'noplaylist': True,
    'cookiefile': 'cookies.txt',  # Certifique-se de que o arquivo está na raiz
    'javascript_filter': True,    # Exige o Node.js que instalamos no Docker
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    
    if not url or not re.match(YOUTUBE_REGEX, url):
        return jsonify({"success": False, "error": "Link inválido."})

    try:
        with yt_dlp.YoutubeDL(BASE_YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string'),
                "success": True
            })
    except Exception as e:
        print(f"Erro no get-info: {str(e)}")
        return jsonify({"success": False, "error": "O YouTube bloqueou o acesso. Verifique os cookies."})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')
    format_type = data.get('format')
    quality = data.get('quality') 
    
    # Copia as opções base e adiciona as específicas de download
    ydl_opts = BASE_YDL_OPTS.copy()
    
    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        })
    else:
        ydl_opts.update({
            'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return jsonify({"success": True, "file_path": filename})
    except Exception as e:
        print(f"Erro no download: {str(e)}")
        return jsonify({"success": False, "error": "Erro na conversão ou bloqueio do YouTube."})

@app.route('/fetch-file')
def fetch_file():
    path = request.args.get('path')
    if os.path.exists(path):
        # Garante que o arquivo seja removido após o envio para o usuário
        return send_file(path, as_attachment=True)
    return "Arquivo não encontrado", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)