import os
import shutil
import subprocess
import tempfile

_CALIBRE = shutil.which("ebook-convert") or "/Applications/calibre.app/Contents/MacOS/ebook-convert"

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
    result = subprocess.run(
        [_CALIBRE, input_path, out_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())
    return out_path


def _tmp_path(src: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = tempfile.mkdtemp()
    return os.path.join(tmp, f"{base}.{ext}")
