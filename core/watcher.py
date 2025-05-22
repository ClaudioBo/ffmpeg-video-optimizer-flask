import os
import time
import shutil
from pathlib import Path
from queue import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.events import notify_disk
from core.config import WATCH_DIR
from core.ffmpeg import process_video
from core.utils import is_video_file
from core.singletons import video_being_processed

task_queue = Queue()
executor = ThreadPoolExecutor(max_workers=int(os.getenv("FFMPEG_WORKERS")))

class VideoHandler(FileSystemEventHandler):
    """Manejador que detecta archivos cerrados y los pone en la cola de procesamiento."""
    def on_closed(self, event):
        if not event.is_directory:
            path = Path(event.src_path)
            if is_video_file(path):
                task_queue.put(path)

def start_video_worker(stop_event):
    """Inicia el worker que toma archivos de la cola y lanza tareas en el executor."""
    def worker_loop():
        while not stop_event.is_set():
            path = task_queue.get()
            if path is None:
                break
            executor.submit(process_video, path)
            time.sleep(0.1)

    thread = Thread(target=worker_loop, args=(stop_event,), daemon=True)
    thread.start()
    return thread

def start_disk_worker(stop_event):
    """Inicia el worker que envia constantemente por SSE el espacio usado en disco."""
    def worker_loop():
        path = WATCH_DIR.resolve()
        while not os.path.ismount(path):
            path = path.parent
        mount_point = path
        while not stop_event.is_set():
            time.sleep(1)
            if len(video_being_processed) == 0:
                continue
            total, used, _ = shutil.disk_usage(mount_point)
            notify_disk(used, total)

    thread = Thread(target=worker_loop, args=(stop_event,), daemon=True)
    thread.start()
    return thread

def start_observer():
    """Configura y arranca el observador de archivos."""
    event_handler = VideoHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=True)
    observer.start()
    return observer

def queue_all_videos():
    """Agrega todos los videos de WATCH_DIR a la cola"""
    for file in WATCH_DIR.rglob("*.mp4"):
        task_queue.put(file)
