from pathlib import Path
from core.config import VIDEO_EXTENSIONS


def get_color(percent):
    """Generar un color en base al porcentaje, interpolando de rojo, naranja y verde"""
    rojo = (220, 53, 69)
    naranja = (255, 193, 7)
    verde = (40, 167, 69)
    if percent < 50:
        ratio = percent / 50
        r = int(rojo[0] + ratio * (naranja[0] - rojo[0]))
        g = int(rojo[1] + ratio * (naranja[1] - rojo[1]))
        b = int(rojo[2] + ratio * (naranja[2] - rojo[2]))
    else:
        ratio = (percent - 50) / 50
        r = int(naranja[0] + ratio * (verde[0] - naranja[0]))
        g = int(naranja[1] + ratio * (verde[1] - naranja[1]))
        b = int(naranja[2] + ratio * (verde[2] - naranja[2]))
    return f"rgb({r},{g},{b})"

def human_readable_size(size_bytes):
    """Convertir bytes a algo humanamente legible"""
    if size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    return f"{size_bytes / (1024**2):.2f} MB"

def is_video_file(path: Path):
    """Checar si es MP4 xd"""
    return path.suffix.lower() in VIDEO_EXTENSIONS