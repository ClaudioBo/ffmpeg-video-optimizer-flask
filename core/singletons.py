from threading import Lock

video_being_processed = {}
video_being_processed_lock = Lock()
sse_clients = []