import subprocess
from threading import Lock

video_being_processed = {}
video_being_processed_lock = Lock()
sse_clients = []

_vainfo_cache = None

def is_amd_gpu():
    global _vainfo_cache

    if _vainfo_cache is None:
        try:
            _vainfo_cache = subprocess.check_output(
                ["vainfo"],
                stderr=subprocess.STDOUT,
                text=True
            )
        except Exception:
            _vainfo_cache = ""

    return (
        "AMD" in _vainfo_cache
        or "Radeon" in _vainfo_cache
        or "RENOIR" in _vainfo_cache
        or "Gallium" in _vainfo_cache
    )
