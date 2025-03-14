from pydantic import BaseModel
import os
import subprocess

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
import yt_dlp
import httpx

# Cookies ka path set karo
cookies_path = os.getenv("COOKIES_PATH", "/opt/render/project/src/app/cookies.txt")
print(f"Cookies Path: {cookies_path}")  # Yeh line add karo

cookies = "SID=g.a000uAh8uWhBiwVmfPnvLoGKed8m1PuIUg-ITw25SuITK9g0vIH1oqbRbWv2NrKIGjynQCG0ZgACgYKAZYSARcSFQHGX2MikQHnF9HLGEsMjvHjKrNidRoVAUF8yKpf4xJps_6MjjM0IZNEPDgS0076; HSID=A0QSgbsEb1Rba-_N3; SSID=A-pgr3Witnyzc9asQ; YSC=Xu6J_R5FWoM; VISITOR_INFO1_LIVE=U05uyeNkYqs"

app = FastAPI()

# Serve HTML page to get location
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Get Exact Location</title>
        <script>
            function getLocation() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(showPosition, showError);
                } else {
                    alert("Geolocation is not supported by this browser.");
                }
            }

            function showPosition(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;

                // Sending lat/lon to backend via POST
                fetch('/send-location', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ latitude: lat, longitude: lon })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
                    document.getElementById('response').innerText = 'Location received! Latitude: ' + data.latitude + ', Longitude: ' + data.longitude;
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }

            function showError(error) {
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        alert('User denied the request for Geolocation.');
                        break;
                    case error.POSITION_UNAVAILABLE:
                        alert('Location information is unavailable.');
                        break;
                    case error.TIMEOUT:
                        alert('The request to get user location timed out.');
                        break;
                    case error.UNKNOWN_ERROR:
                        alert('An unknown error occurred.');
                        break;
                }
            }
        </script>
    </head>
    <body>
        <h2>Get Exact Location using GPS</h2>
        <button onclick="getLocation()">Share Location</button>
        <p id="response"></p>
    </body>
    </html>
    """


# API endpoint to receive location


#@app.get("/send-location")  # Correct FastAPI route
@app.post("/send-location")
async def read_root(request: Request):
    ip = request.headers.get('X-Forwarded-For', request.client.host)
    if ip and ',' in ip:
        ip = ip.split(',')[0].strip()  # ✅ Get first real IP
    
    user_agent = request.headers.get('User-Agent')
    referer = request.headers.get('Referer')
    accept = request.headers.get('Accept')
    content_type = request.headers.get('Content-Type')
    auth_token = request.headers.get('Authorization')
    method = request.method
    cookies = request.cookies

    data = await request.json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # ✅ Use httpx for external API call (async)
    ip_info_url = f"https://ipinfo.io/{ip}/json"
    # Async GET request
    async with httpx.AsyncClient() as client:
        response = await client.get(ip_info_url)
        location_data = response.json()  # Parse JSON response

    return JSONResponse(content={
        "ip": ip,
        "user_agent": user_agent,
        "referer": referer,
        "accept": accept,
        "content_type": content_type,
        "auth_token": auth_token,
        "method": method,
        "cookies": cookies,
        "location_ip_based": location_data,  # IP-based location
        "location_gps_based": {  # GPS-based location from user device
            "latitude": latitude,
            "longitude": longitude
        }
    })

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



