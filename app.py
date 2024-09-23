pip install google-api-python-client yt-dlp pydub
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg

import os
import logging
import subprocess
from googleapiclient.discovery import build
import yt_dlp as youtube_dl
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your API key here
API_KEY = 'AIzaSyA10ghIFZhoQlf3tSN44LPvCdvpkcSFsKw'

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
    try:
        audio = AudioSegment.from_file(input_path, format=audio_format)
        audio.export(output_path, format='mp3')
    except Exception as e:
        logging.error(f"Error during conversion: {e}")
        raise

def hide_file(file_path):
    try:
        subprocess.run(['attrib', '+H', file_path], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error hiding file: {e}")

def display_progress(message):
    # Simple progress indicator
    print(message, end='', flush=True)

def main():
    # Get user input
    song = input("Lied: ")
    artist = input("Artist: ")

    query = f"{song} {artist} lyrics" if artist else f"{song} lyrics"
    search_results = search_youtube(query, API_KEY)

    if not search_results:
        print("No results found.")
        return

    video_id = search_results[0]['id']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Define file paths
    download_dir = r'C:\Users\juebe\Standard-Ordner\Downloads'
    temp_audio_path = os.path.join(download_dir, 'temp_audio.webm')
    
    # Format MP3 filename based on whether artist is provided
    if artist:
        mp3_filename = f"{song} - {artist}.mp3"
    else:
        mp3_filename = f"{song}.mp3"
    
    mp3_path = os.path.join(download_dir, mp3_filename)

    display_progress(f"Downloading video from: {video_url}... ")
    download_youtube_video(video_url, temp_audio_path)

    if not os.path.exists(temp_audio_path):
        print(f"\nFailed to download audio. File not found: {temp_audio_path}")
        return

    # Hide the temporary audio file
    hide_file(temp_audio_path)

    display_progress("Converting audio to MP3... ")
    try:
        convert_audio_to_mp3(temp_audio_path, mp3_path)
        print(f"\nDownloaded and converted to MP3: {mp3_path}")
    except Exception as e:
        print(f"\nError during conversion: {e}")

    # Clean up
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

if __name__ == '__main__':
    main()
