import io
import re
import shutil
import subprocess
import traceback
from pathlib import Path

from .config import OUTPUT_DIR, WATCH_DIR
from .database import log_optimization
from app.events import update_progress, send_reload, notify_clients

from .singletons import video_being_processed, video_being_processed_lock

ffmpeg_time_re = re.compile(r'time=(\d+):(\d+):([\d.]+)')

def parse_ffmpeg_time(s):
    """Obtener del log de FFMPEG en que timestamp del video esta actualmente codificando"""
    match = ffmpeg_time_re.search(s)
    if match:
        h, m, sec = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(sec)
    return None

def get_output_paths(input_path: Path):
    """Generar Paths en base a input_path"""
    rel_path = input_path.relative_to(WATCH_DIR)
    base = rel_path.with_suffix('')
    output_file = OUTPUT_DIR / f"{base}_optimized.mp4"
    failed_file = OUTPUT_DIR / f"{base}_failed.mp4"
    return output_file, failed_file, rel_path.as_posix()

def get_video_duration(input_path: Path) -> float:
    """Usar FFMPEG para obtener la duración total del video"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(input_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error obteniendo duración de {input_path.name}: {e}")
        return 0

def process_video(input_path: Path):
    """Correr FFMPEG para optimizar el video"""
    with video_being_processed_lock:
        video_being_processed[input_path.name] = 0

    try:
        notify_clients()
        output_path, failed_path, rel_path = get_output_paths(input_path)
        tmp_output_path = output_path.with_suffix(output_path.suffix + ".tmp")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if failed_path.exists():
            print(f"Ya existe como fallido: {rel_path}")
            orig_size = input_path.stat().st_size
            log_optimization(rel_path, orig_size, orig_size, failed=1)
            return

        if tmp_output_path.exists():
            tmp_output_path.unlink()

        if not output_path.exists():
            print(f"Procesando: {rel_path}")

            duration = get_video_duration(input_path)
            if duration == 0:
                print("Duración inválida.")
                return

            stderr_buffer = io.StringIO()
            cmd = [
                'ffmpeg', '-y',
                '-hwaccel', 'vaapi', '-vaapi_device', '/dev/dri/renderD128',
                '-i', str(input_path),
                '-vf', 'format=nv12,hwupload',
                '-c:v', 'h264_vaapi', '-bf', '2', '-g', '120',
                '-rc', 'vbr', '-b:v', '0', '-preset', 'fast', '-qp', '29',
                '-c:a', 'copy',
                '-f', 'mp4',
                str(tmp_output_path),
            ]

            try:
                print(f"[INICIO] Ejecutando ffmpeg para {rel_path}")
                orig_size = input_path.stat().st_size
                process = subprocess.Popen(
                    cmd,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                while True:
                    line = process.stderr.readline()
                    if not line:
                        break

                    stderr_buffer.write(line)
                    seconds = parse_ffmpeg_time(line)
                    if seconds is not None:
                        progress = min(100, round((seconds / duration) * 100, 1))
                        update_progress(input_path.name, progress)

                    if tmp_output_path.exists():
                        out_size = tmp_output_path.stat().st_size
                        if out_size > orig_size:
                            print(f"[CANCELADO] El archivo de salida excede al original — {rel_path}")
                            process.terminate()
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                process.kill()
                            tmp_output_path.unlink(missing_ok=True)
                            shutil.copy2(input_path, failed_path)
                            log_optimization(rel_path, orig_size, orig_size, failed=1)
                            return

                process.wait()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, cmd)

                final_output_path = output_path.with_name(output_path.stem + "_optimized" + output_path.suffix)
                tmp_output_path.rename(final_output_path)

                out_size = final_output_path.stat().st_size
                log_optimization(rel_path, orig_size, out_size, failed=0)
                print(f"Optimización exitosa: {final_output_path.relative_to(OUTPUT_DIR)}")

            except subprocess.CalledProcessError:
                print(f"Error al procesar: {rel_path}")
                stderr_output = stderr_buffer.getvalue()
                last_lines = stderr_output.strip().split('\n')[-20:]
                print("\n".join(last_lines))
                traceback.print_exc()
                if tmp_output_path.exists():
                    tmp_output_path.unlink()
                shutil.copy2(input_path, failed_path)
                orig_size = input_path.stat().st_size
                log_optimization(rel_path, orig_size, orig_size, failed=1)
                return
        else:
            print(f"Ya existe: {rel_path} — validando tamaño")

        orig_size = input_path.stat().st_size
        if output_path.exists():
            out_size = output_path.stat().st_size
            if out_size >= orig_size:
                print(f"Archivo más grande: {input_path.name} — reemplazando")
                output_path.unlink()
                shutil.copy2(input_path, failed_path)
                log_optimization(rel_path, orig_size, orig_size, failed=1)
                print(f"Copiado original como: {failed_path.relative_to(OUTPUT_DIR)}")
            else:
                log_optimization(rel_path, orig_size, out_size, failed=0)
                print(f"Optimización exitosa: {output_path.relative_to(OUTPUT_DIR)}")

    except KeyboardInterrupt:
        exit(0)
    except Exception:
        traceback.print_exc()
    finally:
        with video_being_processed_lock:
            video_being_processed.pop(input_path.name, None)
        send_reload()
