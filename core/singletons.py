import subprocess
from threading import Lock

video_being_processed = {}
video_being_processed_lock = Lock()
sse_clients = []

use_hevc = False
try:
    out = subprocess.check_output(["vainfo"], stderr=subprocess.STDOUT, text=True)
    use_hevc = "VAProfileHEVCMain" in out
except Exception:
    pass