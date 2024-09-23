pip install google-api-python-client yt-dlp pydub flask
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg

import os
import logging
import subprocess
from flask import Flask, request, send_file, jsonify
from googleapiclient.discovery import build
import yt_dlp as youtube_dl
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your API key here
API_KEY = 'AIzaSyA10ghIFZhoQlf3tSN44LPvCdvpkcSFsKw'

app = Flask(__name__)

def search_youtube(query, api_key, max_results=1):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

def download_youtube_video(url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True,  # Suppress output
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def convert_audio_to_mp3(input_path, output_path):
    audio_format = input_path.split('.')[-1]
    audio = AudioSegment.from_file(input_path, format=audio_format)
    audio.export(output_path, format='mp3')

@app.route('/download', methods=['GET'])
def download():
    song = request.args.get('song')
    artist = request.args.get('artist', '')

    query = f"{song} {artist} lyrics" if artist else f"{song} lyrics"
    search_results = search_youtube(query, API_KEY)

    if not search_results:
        return jsonify({'error': 'No results found.'}), 404

    video_id = search_results[0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Define file paths
    temp_audio_path = 'temp_audio.webm'
    
    # Format MP3 filename
    mp3_filename = f"{song} - {artist}.mp3" if artist else f"{song}.mp3"
    mp3_path = mp3_filename

    try:
        download_youtube_video(video_url, temp_audio_path)
        convert_audio_to_mp3(temp_audio_path, mp3_path)

        # Clean up the temporary audio file
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        return send_file(mp3_path, as_attachment=True)

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': 'An error occurred during processing.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
