import os
import shutil
import tempfile
import subprocess

_SOFFICE = shutil.which("soffice") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"

_FORMATS: dict[str, list[str]] = {
    "docx": ["pdf", "txt", "html", "odt", "rtf", "epub"],
    "odt":  ["pdf", "txt", "html", "docx", "rtf", "epub"],
    "rtf":  ["pdf", "txt", "html", "docx"],
    "txt":  ["pdf", "html", "docx", "epub"],
    "html": ["pdf", "txt", "docx", "epub"],
    "xlsx": ["pdf", "csv", "odt"],
    "csv":  ["pdf", "xlsx"],
    "pptx": ["pdf"],
    "pdf":  ["txt"],
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower().lstrip(".")
    src_ext = os.path.splitext(input_path)[1].lstrip(".").lower()

    if src_ext == "pdf" and output_ext == "txt":
        return _pdf_to_txt(input_path)

    out_path = _tmp_path(input_path, output_ext)
    _libreoffice(input_path, out_path, output_ext)
    return out_path


def _libreoffice(src: str, dst: str, fmt: str) -> None:
    out_dir = os.path.dirname(dst)
    result = subprocess.run(
        [_SOFFICE, "--headless", "--convert-to", fmt, "--outdir", out_dir, src],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())


def _pdf_to_txt(src: str) -> str:
    out_path = _tmp_path(src, "txt")
    result = subprocess.run(
        ["pdftotext", src, out_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())
    return out_path


def _tmp_path(src: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = tempfile.mkdtemp()
    return os.path.join(tmp, f"{base}.{ext}")
