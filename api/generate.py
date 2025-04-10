from http.client import responses
from gtts import gTTS
from moviepy.editor import *
import requests
import os
import json
import tempfile
import base64
from typing import Dict, Any

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

def handler(request):
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(request.body)
        script = body.get('script')
        vibe = body.get('vibe')
        
        if not script or not vibe:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
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
            
            # Return video data
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'video/mp4',
                    'Content-Disposition': 'attachment; filename="motivational_video.mp4"'
                },
                'body': video_data,
                'isBase64Encoded': True
            }
                
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 