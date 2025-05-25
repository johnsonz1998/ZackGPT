# voice_assistant.py — Local voice assistant with ElevenLabs voice and personality

import os
import platform
import sounddevice as sd
import numpy as np
import whisper
import subprocess
import warnings
import signal
import psutil
import requests
import time
from scipy.io.wavfile import write
from llm.query_assistant import load_index, ask_question

# Config
ELEVENLABS_API_KEY = "sk_478b5b80e4063b5a1436836be71e3563c83bbdb41d856d53"
ELEVENLABS_VOICE_ID = "NFG5qt843uXKj4pFvR7C"
USE_ELEVENLABS = True
VOICE = "Evan (Enhanced)"  # fallback macOS voice
DURATION = 3
SAMPLE_RATE = 16000
TEMP_FILENAME = "temp.wav"

# Suppress FP16 CPU warning from Whisper
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.transcribe")

# Init
whisper_model = whisper.load_model("tiny")
index = load_index()
say_process = None

def speak(text):
    if USE_ELEVENLABS:
        speak_elevenlabs(text)
    else:
        speak_mac(text)

def speak_mac(text):
    global say_process
    say_process = subprocess.Popen(["say", "-v", VOICE, text])
    say_process.wait()
    time.sleep(1.0)

def play_audio(filename="output.mp3"):
    if platform.system() == "Darwin":
        subprocess.run(["afplay", filename])
    else:
        subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def speak_elevenlabs(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=payload, headers=headers, stream=True)
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        play_audio("output.mp3")
        time.sleep(1.0)
    else:
        print("❌ ElevenLabs error:", response.status_code, response.text)
        speak_mac("Something went wrong with ElevenLabs.")

def stop_speaking():
    global say_process
    if say_process and say_process.poll() is None:
        parent = psutil.Process(say_process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

# Main loop
print("🎙️ Voice assistant is active. Speak now...")

try:
    while True:
        print("\n🎤 Listening...")
        recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
        sd.wait()
        write(TEMP_FILENAME, SAMPLE_RATE, recording)

        print("🧠 Transcribing...")
        result = whisper_model.transcribe(TEMP_FILENAME)
        user_question = result['text'].strip()
        print(f"You said: {user_question}")

        if not user_question:
            print("🤔 Didn't catch that. Try again.")
            speak("Didn't catch that. Try again.")
            continue

        if user_question.lower() in {"quit", "exit"}:
            speak("Shutting down.")
            break

        try:
            custom_prompt = (
                "You are Zach’s sarcastic AI assistant. Be short, helpful, and a little bit cocky.\n\n"
                f"User: {user_question}\nAssistant:"
            )
            response = ask_question(index, custom_prompt)
            print(f"💬 Assistant: {response}")
            speak(response)

        except Exception as e:
            print(f"⚠️ Assistant error: {e}")
            speak("Something went wrong. Check your logs.")
            continue

except KeyboardInterrupt:
    stop_speaking()
    print("⛔ Interrupted. Voice playback stopped.")

print("👋 Voice assistant closed.")
