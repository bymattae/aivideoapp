from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from gtts import gTTS
from moviepy.editor import *
import requests
import os
import uuid
from typing import List
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
TEMP_DIR = "temp"

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generate_voiceover(text: str, output_path: str):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(output_path)

def fetch_stock_videos(keyword: str, count: int = 5) -> List[str]:
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page={count}&orientation=portrait"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch videos from Pexels")
    
    videos = response.json().get("videos", [])
    video_urls = []
    
    for video in videos:
        video_files = video.get("video_files", [])
        for file in video_files:
            if file.get("height", 0) >= 1080:  # Get highest quality
                video_urls.append(file.get("link"))
                break
    
    return video_urls

def download_video(url: str, output_path: str):
    response = requests.get(url)
    with open(output_path, "wb") as f:
        f.write(response.content)

def create_motivational_video(script: str, vibe: str) -> str:
    # Generate unique ID for this session
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Generate voiceover
    voiceover_path = os.path.join(session_dir, "voiceover.mp3")
    generate_voiceover(script, voiceover_path)
    
    # Fetch and download stock videos
    video_urls = fetch_stock_videos(vibe)
    video_paths = []
    
    for i, url in enumerate(video_urls):
        video_path = os.path.join(session_dir, f"stock_{i}.mp4")
        download_video(url, video_path)
        video_paths.append(video_path)
    
    # Load all video clips
    clips = [VideoFileClip(path) for path in video_paths]
    
    # Concatenate videos
    final_video = concatenate_videoclips(clips)
    
    # Add voiceover
    audio = AudioFileClip(voiceover_path)
    final_video = final_video.set_audio(audio)
    
    # Add text overlay (first sentence)
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
    output_path = os.path.join(session_dir, "final.mp4")
    final_video.write_videofile(output_path, fps=24)
    
    # Clean up
    for clip in clips:
        clip.close()
    final_video.close()
    
    return output_path

@app.post("/generate")
async def generate_video(script: str, vibe: str):
    try:
        output_path = create_motivational_video(script, vibe)
        return {"success": True, "video_path": output_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{video_path:path}")
async def download_video(video_path: str):
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4", filename="motivational_video.mp4")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 