# gunicorn_conf.py
import threading,time
import datetime
from main import refresh_data


def loop():
    while True:
        now = datetime.datetime.now().time()
        start_time = time(23, 0)   # 23:00
        end_time = time(0, 30)     # 00:30

        if not start_time <= now or not now <= end_time:
            refresh_data()
            time.sleep(600)

def start_background_task():
    background_thread = threading.Thread(target=loop, name="BackgroundTask")
    background_thread.daemon = True
    background_thread.start()
    print("Background task started.")

def on_starting(server):
    start_background_task()
