from pydantic import BaseModel
import os
import subprocess

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

# Cookies ka path set karo
cookies_path = os.getenv("COOKIES_PATH", "/app/cookies.txt")
print(f"Cookies Path: {cookies_path}")  # Yeh line add karo

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": cookies_path, "ServerStatus": "Server is running"}

@app.get("/extract")
def extract_url(video_url: str = Query(..., description="YouTube video URL")):
    try:
        ydl_opts = {
            'format': 'best',
            #'cookiefile': 'cookies.txt',  # Pass the cookies for authentication
            'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_url = info['url']
            return {"success": True, "video_url": video_url}
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=400)





# Playback URL extract karne ka GET endpoint
@app.get("/extract-url/")
def extract_playback_url(video_url: str):
    try:
        command = [
            "yt-dlp",
            "--cookies", cookies_path,
            "--get-url",
            video_url
        ]

        result = subprocess.run(command, text=True, capture_output=True)

        if result.returncode == 0:
            playback_url = result.stdout.strip()
            return {"status": "success", "playback_url": playback_url}
        else:
            return {"status": "error", "message": result.stderr}

    except Exception as e:
        return {"status": "error", "message": str(e)}





# Yt-dlp se playback URL extract kar rahe hain
def get_playback_url(video_url):
    try:
        output = subprocess.check_output([
            "yt-dlp",
            "--cookies", cookies_path,
            "-g", video_url
        ]).decode("utf-8").strip()

        return output
    except Exception as e:
        return str(e)



