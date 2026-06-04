import os
import shutil
import subprocess
import sys
import tempfile

_CALIBRE = shutil.which("ebook-convert") or "/Applications/calibre.app/Contents/MacOS/ebook-convert"
_XVFB = shutil.which("xvfb-run")

_FORMATS: dict[str, list[str]] = {
    "epub": ["pdf", "mobi", "azw3", "fb2", "txt", "html", "docx"],
    "mobi": ["epub", "pdf", "txt", "html"],
    "azw3": ["epub", "pdf", "txt", "mobi"],
    "fb2":  ["epub", "pdf", "txt"],
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower().lstrip(".")
    out_path = _tmp_path(input_path, output_ext)

    cmd = [_CALIBRE, input_path, out_path]
    # PDF output uses Qt WebEngine which needs a display on headless Linux
    if output_ext == "pdf" and sys.platform != "darwin" and _XVFB:
        cmd = [_XVFB, "-a"] + cmd

    env = os.environ.copy()
    if output_ext == "pdf" and sys.platform != "darwin":
        env.setdefault("QT_QPA_PLATFORM", "offscreen")

    result = subprocess.run(cmd, capture_output=True, env=env)
    stderr = result.stderr.decode("utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(stderr)
    if not os.path.exists(out_path):
        stdout = result.stdout.decode("utf-8", errors="replace")
        raise RuntimeError(f"Calibre produced no output.\nstdout: {stdout}\nstderr: {stderr}")
    return out_path


def _tmp_path(src: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = tempfile.mkdtemp()
    return os.path.join(tmp, f"{base}.{ext}")
