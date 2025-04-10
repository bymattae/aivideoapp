from http.client import responses
from gtts import gTTS
from moviepy.editor import *
import requests
import os
import json
import tempfile
import base64
from typing import Dict, Any
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def generate_voiceover(text: str, output_path: str):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)

def fetch_stock_videos(keyword: str, count: int = 5) -> list:
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page={count}&orientation=portrait"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception("Failed to fetch videos from Pexels")
    
    videos = response.json().get("videos", [])
    video_urls = []
    
    for video in videos:
        video_files = video.get("video_files", [])
        for file in video_files:
            if file.get("height", 0) >= 1080:
                video_urls.append(file.get("link"))
                break
    
    return video_urls

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            script = data.get('script')
            vibe = data.get('vibe')
            
            if not script or not vibe:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing required fields'}).encode())
                return
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate voiceover
                voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
                generate_voiceover(script, voiceover_path)
                
                # Fetch and download stock videos
                video_urls = fetch_stock_videos(vibe)
                video_paths = []
                
                for i, url in enumerate(video_urls):
                    video_path = os.path.join(temp_dir, f"stock_{i}.mp4")
                    response = requests.get(url)
                    with open(video_path, "wb") as f:
                        f.write(response.content)
                    video_paths.append(video_path)
                
                # Process video
                clips = [VideoFileClip(path) for path in video_paths]
                final_video = concatenate_videoclips(clips)
                
                # Add voiceover
                audio = AudioFileClip(voiceover_path)
                final_video = final_video.set_audio(audio)
                
                # Add text overlay
                first_sentence = script.split('.')[0] + '.'
                txt_clip = TextClip(first_sentence, fontsize=70, color='white', font='Arial-Bold')
                txt_clip = txt_clip.set_position('center').set_duration(5)
                final_video = CompositeVideoClip([final_video, txt_clip])
                
                # Resize to 9:16
                final_video = final_video.resize(height=1920, width=1080)
                
                # Add fade in/out
                final_video = final_video.crossfadein(1).crossfadeout(1)
                
                # Ensure video is under 60 seconds
                if final_video.duration > 60:
                    final_video = final_video.subclip(0, 60)
                
                # Save final video
                output_path = os.path.join(temp_dir, "final.mp4")
                final_video.write_videofile(output_path, fps=24)
                
                # Read the video file and encode as base64
                with open(output_path, 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                
                # Clean up
                for clip in clips:
                    clip.close()
                final_video.close()
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Disposition', 'attachment; filename="motivational_video.mp4"')
                self.end_headers()
                self.wfile.write(base64.b64decode(video_data))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

def handler(event, context):
    return Handler.do_POST(Handler) 