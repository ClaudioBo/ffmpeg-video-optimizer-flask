from core.database import init_db
from core.watcher import start_disk_worker, start_observer, start_video_worker
from app import create_app
import threading
import time

def main():
    """Inicializar base de datos, observador, worker de ffmpeg, y Flash"""
    init_db()
    observer = start_observer()
    start_video_worker()
    start_disk_worker()
    app = create_app()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=80), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
