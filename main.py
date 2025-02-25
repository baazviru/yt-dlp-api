from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "YT-DLP API is running!"}

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

