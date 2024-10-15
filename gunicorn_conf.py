# gunicorn_conf.py
import threading,time
import datetime
from main import refresh_data


def loop():
    while True:
        start_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '0:30', '%Y-%m-%d%H:%M')
        end_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:00', '%Y-%m-%d%H:%M')

        now_time = datetime.datetime.now()

        if start_time < now_time < end_time:
            refresh_data()
            time.sleep(600)

def start_background_task():
    background_thread = threading.Thread(target=loop, name="BackgroundTask")
    background_thread.daemon = True
    background_thread.start()
    print("Background task started.")

def on_starting(server):
    start_background_task()
