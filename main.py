from core.database import init_db
from core.watcher import start_disk_worker, start_observer, start_video_worker, executor
from app import create_app
import threading
import time


def main():
    """Inicializar base de datos, observador, worker de ffmpeg, y Flash"""
    init_db()
    stop_event = threading.Event()
    app = create_app()
    observer_thread = start_observer()
    video_thread = start_video_worker(stop_event)
    disk_thread = start_disk_worker(stop_event)
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=80), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nCTRL+C detectado! Deteniendo...")
        stop_event.set()
        executor.shutdown(wait=False)

        observer_thread.stop()
        observer_thread.join()
        video_thread.join()
        disk_thread.join()

        print("Todos los procesos detenidos, saliendo...")


if __name__ == "__main__":
    main()
