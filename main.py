from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "YT-DLP API is running!"}

@app.get("/extract")
def extract(url: str = Query(...)):
    try:
        ydl_opts = {'format': 'best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        return {"error": str(e)}
