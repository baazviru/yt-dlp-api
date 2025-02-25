from pydantic import BaseModel
import os
import subprocess

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

# Cookies ka path set karo
cookies_path = os.getenv("COOKIES_PATH", "/opt/render/project/src/app/cookies.txt")
print(f"Cookies Path: {cookies_path}")  # Yeh line add karo

cookies = "SID=g.a000uAh8uWhBiwVmfPnvLoGKed8m1PuIUg-ITw25SuITK9g0vIH1oqbRbWv2NrKIGjynQCG0ZgACgYKAZYSARcSFQHGX2MikQHnF9HLGEsMjvHjKrNidRoVAUF8yKpf4xJps_6MjjM0IZNEPDgS0076; HSID=A0QSgbsEb1Rba-_N3; SSID=A-pgr3Witnyzc9asQ; YSC=Xu6J_R5FWoM; VISITOR_INFO1_LIVE=U05uyeNkYqs"

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
            "--cookies", cookies,
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





class VideoURL(BaseModel):
    url: str

# Playback URL extract karne ka endpoint
@app.get("/playback-url/")
def get_playback_url(video_url: str):
    try:
        output = subprocess.check_output([
            "yt-dlp",
            "--cookies", cookies,
            "-g", video_url
        ]).decode("utf-8").strip()

        return {"status": "success", "playback_url": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/mypath/")
def get_playback_url(video_url: str):
    try:
        # Read the cookies content
        with open(cookies_path, "r") as f:
            cookies_content = cookies

        # Pass cookies as a header
        output = subprocess.check_output([
            "yt-dlp",
            f"--add-header", f"Cookie: {cookies_content}",
            "-g", video_url
        ]).decode("utf-8").strip()

        return {"status": "success", "playback_url": output}
    except Exception as e:
        return {"status": "error", "message": str(e)}



