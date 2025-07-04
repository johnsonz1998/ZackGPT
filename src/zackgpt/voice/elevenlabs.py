import requests
import subprocess
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from config import config
import platform

def speak(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}/stream"
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": config.ELEVENLABS_STABILITY,
            "similarity_boost": config.ELEVENLABS_SIMILARITY
        }
    }

    response = requests.post(url, json=payload, headers=headers, stream=True)
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        if platform.system() == "Darwin":
            subprocess.run(["afplay", "output.mp3"])
        else:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "output.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
    else:
        print("❌ ElevenLabs error:", response.status_code, response.text)