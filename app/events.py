import json
from core.singletons import video_being_processed, video_being_processed_lock, sse_clients
from queue import Queue

def update_progress(filename, progress):
    """Actualiza el progreso de un archivo en proceso."""
    with video_being_processed_lock:
        video_being_processed[filename] = progress
    notify_progress()

def notify_progress():
    """Envía el estado actual a todos los clientes conectados por SSE."""
    with video_being_processed_lock:
        payload = json.dumps({
            "type": "status",
            "processing": [
                {"filename": f, "progress": video_being_processed.get(f, 0)}
                for f in video_being_processed
            ]
        })

    for q in sse_clients:
        q.put(payload)

def notifY_reload():
    """Notifica a los clientes que deben recargar la interfaz."""
    payload = json.dumps({"type": "reload"})
    for q in sse_clients:
        q.put(payload)

def notify_disk(used, total):
    """Notifica a los clientes el uso del disco."""
    payload = json.dumps({"type": "disk", "used": used, "total": total})
    for q in sse_clients:
        q.put(payload)

def get_initial_status():
    """Devuelve el estado inicial para un nuevo cliente SSE."""
    with video_being_processed_lock:
        return json.dumps({
            "type": "status",
            "processing": [
                {"filename": f, "progress": video_being_processed.get(f, 0)}
                for f in video_being_processed
            ]
        })

def register_client():
    """Registra un nuevo cliente SSE y devuelve su cola de mensajes y estado inicial."""
    q = Queue()
    sse_clients.append(q)
    initial = get_initial_status()
    return q, initial

def unregister_client(q):
    """Elimina un cliente desconectado de la lista de SSE."""
    if q in sse_clients:
        sse_clients.remove(q)
