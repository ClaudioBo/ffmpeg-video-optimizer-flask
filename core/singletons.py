import subprocess
from threading import Lock

video_being_processed = {}
video_being_processed_lock = Lock()
sse_clients = []

is_amd = False
try:
    vainfo = subprocess.check_output(["vainfo"], stderr=subprocess.STDOUT, text=True)
    is_amd = "Gallium" in vainfo or "Radeon" in vainfo
except Exception:
    pass