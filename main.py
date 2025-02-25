import subprocess
from fastapi import FastAPI

app = FastAPI()

@app.get("/get_video_url/")
def get_video_url(video_id: str):
    try:
        # Run yt-dlp command with cookies
        result = subprocess.run(
            ["yt-dlp", "-g", f"https://www.youtube.com/watch?v={video_id}", "--cookies", "cookies.txt"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            video_url = result.stdout.strip()
            return {"video_url": video_url}
        else:
            return {"error": result.stderr.strip()}
    except Exception as e:
        return {"error": str(e)}
