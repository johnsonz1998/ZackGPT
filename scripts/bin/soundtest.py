# scripts/tools/soundtest.py

import sounddevice as sd
from scipy.io.wavfile import write

print("🎙️ Recording 3 seconds...")

sample_rate = 16000
duration = 3  # seconds

recording = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, dtype='int16')
sd.wait()

write("test.wav", sample_rate, recording)
print("✅ Saved test.wav")
