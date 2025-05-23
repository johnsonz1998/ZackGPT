import subprocess
import time
import config
import psutil

say_process = None

def speak(text):
    global say_process
    say_process = subprocess.Popen(["say", "-v", config.MACOS_VOICE, text])
    say_process.wait()
    time.sleep(1.0)

def stop_speaking():
    global say_process
    if say_process and say_process.poll() is None:
        parent = psutil.Process(say_process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
