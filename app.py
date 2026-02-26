from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import re

app = Flask(__name__)

# Configuração de pastas
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- CONFIGURAÇÃO MANUAL DO FFMPEG ---
# Certifique-se de que a pasta 'bin' está dentro de C:/ffmpeg
FFMPEG_PATH = 'ffmpeg' 

# Validação de Segurança (Apenas links oficiais do YouTube)
YOUTUBE_REGEX = r"^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    
    if not url or not re.match(YOUTUBE_REGEX, url):
        return jsonify({"success": False, "error": "Link inválido. Insira um URL do YouTube."})

    ydl_opts = {'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration_string'),
                "success": True
            })
    except Exception:
        return jsonify({"success": False, "error": "Vídeo indisponível ou protegido."})

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    video_url = data.get('url')
    format_type = data.get('format')
    quality = data.get('quality') 
    
    if not re.match(YOUTUBE_REGEX, video_url):
        return jsonify({"success": False, "error": "Ação bloqueada por segurança."})

    if format_type == 'mp3':
        ydl_opts = {
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'keepvideo': False,
        }
    else:
        ydl_opts = {
            'ffmpeg_location': FFMPEG_PATH,
            'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'restrictfilenames': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            temp_filename = ydl.prepare_filename(info)
            
            if format_type == 'mp3':
                filename = os.path.splitext(temp_filename)[0] + '.mp3'
            else:
                filename = temp_filename
            
            if os.path.exists(filename):
                return jsonify({"success": True, "file_path": filename})
            return jsonify({"success": False, "error": "Falha ao gerar arquivo."})
                
    except Exception as e:
        return jsonify({"success": False, "error": "Erro no servidor. Tente uma qualidade menor."})

@app.route('/fetch-file')
def fetch_file():
    path = request.args.get('path')
    if os.path.exists(path) and path.startswith(DOWNLOAD_FOLDER):
        response = send_file(path, as_attachment=True)
        @response.call_on_close
        def remove_file():
            try: os.remove(path)
            except: pass
        return response
    return "Erro", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)