import json
import os
from queue import Queue
import shutil
from flask import Blueprint, render_template, redirect, url_for, Response

from core.config import WATCH_DIR
from core.database import clear_optimizations, get_optimizations
from core.utils import get_color, human_readable_size
from core.watcher import queue_all_videos
from core.ffmpeg import clear_originals
from core.singletons import video_being_processed, video_being_processed_lock, sse_clients


routes = Blueprint("routes", __name__)

@routes.route("/")
def index():
    rows = get_optimizations()

    total_orig_bytes = 0
    total_opt_bytes = 0
    data_converted = []

    for filename, orig_mb, opt_mb, percent, failed in rows:
        orig_mb = float(orig_mb)
        opt_mb = float(opt_mb)
        orig_bytes = orig_mb * 1024 * 1024
        opt_bytes = opt_mb * 1024 * 1024
        total_orig_bytes += orig_bytes
        total_opt_bytes += opt_bytes
        color = get_color(percent) if not failed else None
        data_converted.append((
            filename,
            human_readable_size(orig_bytes),
            orig_bytes,
            human_readable_size(opt_bytes),
            opt_bytes,
            percent,
            failed,
            color,
            percent
        ))

    total_orig_str = human_readable_size(total_orig_bytes)
    total_opt_str = human_readable_size(total_opt_bytes)

    return render_template(
        'index.html',
        data=data_converted,
        total_orig=total_orig_str,
        total_opt=total_opt_str
    )

@routes.route("/manual_scan", methods=['POST'])
def manual_scan():
    print("Escaneo manual iniciado...")
    queue_all_videos()
    return redirect(url_for('routes.index'))

@routes.route("/delete_stats", methods=['POST'])
def delete_stats():
    print("Eliminando estadísticas...")
    clear_optimizations()
    return redirect(url_for('routes.index'))

@routes.route("/delete_originals", methods=['POST'])
def delete_originals():
    print("Eliminando videos originales que ya hayan sido procesados...")
    clear_originals()
    return redirect(url_for('routes.index'))

@routes.route("/events")
def sse():
    def event_stream():
        q = Queue()
        sse_clients.append(q)

        with video_being_processed_lock:
            initial_payload = json.dumps({
                "type": "status",
                "processing": [
                    {"filename": f, "progress": video_being_processed.get(f, 0)}
                    for f in video_being_processed
                ]
            })
        yield f"data: {initial_payload}\n\n"

        path = WATCH_DIR.resolve()
        while not os.path.ismount(path):
            path = path.parent
        mount_point = path
        total, used, _ = shutil.disk_usage(mount_point)
        usage_json = json.dumps({"type": "disk", "used": used, "total": total})
        yield f"data: {usage_json}\n\n"

        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            sse_clients.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")
