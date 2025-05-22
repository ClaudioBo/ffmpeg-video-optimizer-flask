import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

WATCH_DIR = Path(os.getenv("WATCH_DIR"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR"))
FFMPEG_WORKERS = int(os.getenv("FFMPEG_WORKERS"))
DB_PATH = Path("./data.db")
VIDEO_EXTENSIONS = ['.mp4']
