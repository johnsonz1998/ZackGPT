# scripts/watch_main.py

import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os

class RestartHandler(FileSystemEventHandler):
    def __init__(self, command, watch_path):
        self.command = command
        self.watch_path = watch_path
        self.process = subprocess.Popen(self.command)

    def on_any_event(self, event):
        if event.is_directory:
            return
        print("🔁 Detected change, restarting...")
        self.process.kill()
        self.process = subprocess.Popen(self.command)

    def cleanup(self):
        self.process.kill()

if __name__ == "__main__":
    cmd = ["python", "-m", "scripts.startup.main"]
    event_handler = RestartHandler(cmd, watch_path="scripts")
    observer = Observer()
    observer.schedule(event_handler, path="scripts", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.cleanup()

    observer.join()
