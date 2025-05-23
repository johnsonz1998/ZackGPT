import numpy as np
import config
import webrtcvad
from scipy.io.wavfile import write
from datetime import datetime 
import logging
from pathlib import Path
log_debug = logging.getLogger("zackgpt").debug

# Globals
whisper_model = None
engine_type = config.TRANSCRIBE_ENGINE
MIN_FRAMES = 10

def reload_whisper_model():
    """Reload Whisper or FasterWhisper model based on config."""
    global whisper_model, engine_type
    engine_type = config.TRANSCRIBE_ENGINE

    if engine_type == "openai-whisper":
        import whisper
        whisper_model = whisper.load_model(config.WHISPER_MODEL)
        log_debug(f"Reloaded OpenAI Whisper model: {config.WHISPER_MODEL}")
    else:
        from faster_whisper import WhisperModel
        whisper_model = WhisperModel(config.WHISPER_MODEL, compute_type="int8")
        log_debug(f"Reloaded FasterWhisper model: {config.WHISPER_MODEL}")

# Load on import
reload_whisper_model()

def transcribe_audio(audio_np, sample_rate=16000):
    """Transcribe audio using the selected model and log result."""
    try:
        if engine_type == "openai-whisper":
            write(config.TEMP_AUDIO_FILE, sample_rate, audio_np)
            result = whisper_model.transcribe(str(config.TEMP_AUDIO_FILE))
            if config.TEMP_AUDIO_FILE.exists():
                config.TEMP_AUDIO_FILE.unlink()
            text = result.get("text", "").strip()

        else:
            audio_np = audio_np.astype("float32") / 32768.0
            segments, _ = whisper_model.transcribe(audio_np, language="en")
            text = "".join([seg.text for seg in segments if seg.text]).strip()

        if text:
            _log_transcription(text)

        return text

    except Exception as e:
        log_error(f"Transcription failed: {e}")
        return ""

def _log_transcription(text):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = config.TRANSCRIBE_LOG_DIR / f"{timestamp}.txt"

    try:
        config.TRANSCRIBE_LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(log_file, "w") as f:
            f.write(text.strip() + "\n")
    except Exception as e:
        log_error(f"Failed to write transcription log: {e}")

def listen_for_audio(duration=None, sample_rate=None):
    """Record for a fixed duration and transcribe."""
    duration = duration or config.RECORD_DURATION
    sample_rate = sample_rate or config.SAMPLE_RATE

    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()

    return transcribe_audio(recording)

def listen_until_silence(sample_rate=16000, aggressiveness=1, silence_duration=1.2):
    """Listen until silence using VAD and transcribe the result."""
    vad = webrtcvad.Vad(aggressiveness)
    frame_duration = 20
    frame_size = int(sample_rate * frame_duration / 1000)
    silence_threshold = int((silence_duration * 1000) / frame_duration)

    buffer = []
    silence_count = 0

    try:
        with sd.RawInputStream(samplerate=sample_rate, blocksize=frame_size,
                               dtype='int16', channels=1) as stream:
            while True:
                audio_bytes, _ = stream.read(frame_size)
                is_speech = vad.is_speech(audio_bytes, sample_rate)
                frame_array = np.frombuffer(audio_bytes, dtype=np.int16)

                if is_speech:
                    buffer.append(frame_array)
                    silence_count = 0
                elif buffer and len(buffer) >= MIN_FRAMES:
                    silence_count += 1
                    if silence_count >= silence_threshold:
                        break
    except KeyboardInterrupt:
        return ""

    audio_np = np.concatenate(buffer)
    return transcribe_audio(audio_np)

def listen_once(duration=None):
    return listen_for_audio(duration=duration)

# Exports
__all__ = ["listen_once", "listen_for_audio", "listen_until_silence", "reload_whisper_model", "whisper_model"]