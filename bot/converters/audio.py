import os
import subprocess
import tempfile

_FORMATS: dict[str, list[str]] = {
    "mp3":  ["flac", "ogg", "wav", "m4a", "aac", "opus"],
    "flac": ["mp3", "ogg", "wav", "m4a"],
    "ogg":  ["mp3", "flac", "wav", "m4a"],
    "wav":  ["mp3", "flac", "ogg", "m4a", "aac"],
    "m4a":  ["mp3", "flac", "ogg", "wav"],
    "aac":  ["mp3", "flac", "ogg", "wav", "m4a"],
    "wma":  ["mp3", "flac", "ogg", "wav"],
    "opus": ["mp3", "ogg", "wav"],
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower().lstrip(".")
    out_path = _tmp_path(input_path, output_ext)
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, out_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())
    return out_path


def _tmp_path(src: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = tempfile.mkdtemp()
    return os.path.join(tmp, f"{base}.{ext}")
