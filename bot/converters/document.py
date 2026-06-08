import os
import shutil
import tempfile
import subprocess
import threading
import zipfile

_SOFFICE = shutil.which("soffice") or "/Applications/LibreOffice.app/Contents/MacOS/soffice"
_SOFFICE_LOCK = threading.Lock()

_FORMATS: dict[str, list[str]] = {
    "docx": ["pdf", "txt", "html", "odt", "rtf", "epub"],
    "odt":  ["pdf", "txt", "html", "docx", "rtf", "epub"],
    "rtf":  ["pdf", "txt", "html", "docx"],
    "txt":  ["pdf", "html", "docx", "epub"],
    "html": ["pdf", "txt", "docx", "epub"],
    "xlsx": ["pdf", "csv", "odt"],
    "csv":  ["pdf", "xlsx"],
    "pptx": ["pdf"],
    "pdf":  ["docx", "txt", "jpg", "png", "html"],
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower().lstrip(".")
    src_ext = os.path.splitext(input_path)[1].lstrip(".").lower()

    if src_ext == "pdf":
        if output_ext == "txt":
            return _pdf_to_txt(input_path)
        if output_ext in ("jpg", "png"):
            return _pdf_to_images(input_path, output_ext)
        if output_ext in ("docx", "html"):
            out_path = _tmp_path(input_path, output_ext)
            _libreoffice(input_path, out_path, output_ext)
            return out_path

    out_path = _tmp_path(input_path, output_ext)
    _libreoffice(input_path, out_path, output_ext)
    return out_path


def _libreoffice(src: str, dst: str, fmt: str) -> None:
    out_dir = os.path.dirname(dst)
    cmd = [_SOFFICE, "--headless", "--convert-to", fmt, "--outdir", out_dir]
    if os.path.splitext(src)[1].lstrip(".").lower() == "pdf":
        cmd += ["--infilter=writer_pdf_import"]
    cmd.append(src)
    with _SOFFICE_LOCK:
        result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())
    # LibreOffice may produce a file with a sanitized name — find and rename it
    matches = [f for f in os.listdir(out_dir) if f.lower().endswith(f".{fmt}")]
    if not matches:
        raise RuntimeError(f"LibreOffice produced no .{fmt} output")
    actual = os.path.join(out_dir, matches[0])
    if actual != dst:
        os.rename(actual, dst)


def _pdf_to_images(src: str, fmt: str) -> str:
    out_dir = tempfile.mkdtemp()
    prefix = os.path.join(out_dir, "page")
    flag = "-jpeg" if fmt == "jpg" else "-png"
    result = subprocess.run(
        ["pdftoppm", flag, src, prefix],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

    pages = sorted(f for f in os.listdir(out_dir) if not f.endswith(".zip"))
    if not pages:
        raise RuntimeError("pdftoppm produced no output")

    base = os.path.splitext(os.path.basename(src))[0]
    if len(pages) == 1:
        out_path = os.path.join(out_dir, f"{base}.{fmt}")
        os.rename(os.path.join(out_dir, pages[0]), out_path)
        return out_path

    zip_path = os.path.join(tempfile.mkdtemp(), f"{base}_pages.zip")
    with zipfile.ZipFile(zip_path, "w") as zf:
        for page in pages:
            zf.write(os.path.join(out_dir, page), page)
    return zip_path


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
