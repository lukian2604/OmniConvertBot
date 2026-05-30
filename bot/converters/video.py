import os
import tempfile
import subprocess

_FORMATS: dict[str, list[str]] = {
    "mp4":  ["avi", "mov", "webm", "mkv", "gif", "mp3"],
    "avi":  ["mp4", "mov", "webm", "mkv", "mp3"],
    "mov":  ["mp4", "avi", "webm", "mkv", "mp3"],
    "webm": ["mp4", "avi", "mov", "mkv", "mp3"],
    "mkv":  ["mp4", "avi", "mov", "webm", "mp3"],
    "flv":  ["mp4", "avi", "mov", "mp3"],
    "wmv":  ["mp4", "avi", "mov", "mp3"],
    "mpeg": ["mp4", "avi", "mov"],
    "3gp":  ["mp4", "avi"],
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower().lstrip(".")
    out_path = _tmp_path(input_path, output_ext)

    if output_ext == "gif":
        _to_gif(input_path, out_path)
    elif output_ext == "mp3":
        _extract_audio(input_path, out_path)
    else:
        _ffmpeg(input_path, out_path)

    return out_path


def _ffmpeg(src: str, dst: str) -> None:
    cmd = ["ffmpeg", "-y", "-i", src, dst]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())


def _to_gif(src: str, dst: str) -> None:
    palette = dst + "_palette.png"
    subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-vf", "fps=10,scale=480:-1:flags=lanczos,palettegen", palette],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-i", palette,
         "-filter_complex", "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse", dst],
        capture_output=True, check=True,
    )
    os.remove(palette)


def _extract_audio(src: str, dst: str) -> None:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=codec_type", "-of", "default=noprint_wrappers=1", src],
        capture_output=True,
    )
    if b"codec_type=audio" not in probe.stdout:
        raise ValueError("Video has no audio stream")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-q:a", "0", "-map", "a", dst],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())


def _tmp_path(src: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = tempfile.mkdtemp()
    return os.path.join(tmp, f"{base}.{ext}")
