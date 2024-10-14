# gunicorn_conf.py
import threading
import time
from main import refresh_data


def loop():
    while True:
        refresh_data()
        time.sleep(600)

def start_background_task():
    background_thread = threading.Thread(target=loop, name="BackgroundTask")
    background_thread.daemon = True
    background_thread.start()
    print("Background task started.")

def on_starting(server):
    start_background_task()
