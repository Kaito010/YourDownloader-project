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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    
    if not url or not re.match(YOUTUBE_REGEX, url):
        return jsonify({"success": False, "error": "Link inválido."})

    # User-agent ajuda a evitar bloqueios do YouTube no servidor
    ydl_opts = {
    'quiet': True,
    'noplaylist': True,
    'cookiefile': 'cookies.txt',
    # Força o uso do Node.js que instalamos no build.sh
    'javascript_filter': True, 
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string'),
                "success": True
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')
    format_type = data.get('format')
    quality = data.get('quality') 
    
    if format_type == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return jsonify({"success": True, "file_path": filename})
    except Exception as e:
        return jsonify({"success": False, "error": "Erro na conversão. Verifique o FFmpeg."})

@app.route('/fetch-file')
def fetch_file():
    path = request.args.get('path')
    if os.path.exists(path):
        response = send_file(path, as_attachment=True)
        @response.call_on_close
        def remove_file():
            try: os.remove(path)
            except: pass
        return response
    return "Arquivo não encontrado", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)