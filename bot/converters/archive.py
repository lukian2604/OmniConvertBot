import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

_UNAR = shutil.which("unar") or "/opt/homebrew/bin/unar"
_7Z = shutil.which("7z") or "/opt/homebrew/bin/7z"
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}

_FORMATS: dict[str, list[str]] = {
    "zip":     ["tar.gz", "tar.bz2", "7z"],
    "rar":     ["zip", "tar.gz", "tar.bz2", "7z"],
    "7z":      ["zip", "tar.gz", "tar.bz2"],
    "tar.gz":  ["zip", "7z"],
    "tar.bz2": ["zip", "7z"],
    "cbr":     ["cbz", "pdf"],
    "cbz":     ["pdf"],
    "cb7":     ["cbz", "pdf"],
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower()
    tmp_extract = tempfile.mkdtemp()

    result = subprocess.run(
        [_UNAR, "-output-directory", tmp_extract, "-force-overwrite", input_path],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

    contents = os.listdir(tmp_extract)
    if len(contents) == 1 and os.path.isdir(os.path.join(tmp_extract, contents[0])):
        extract_dir = os.path.join(tmp_extract, contents[0])
    else:
        extract_dir = tmp_extract

    base = _base_name(input_path)
    out_dir = tempfile.mkdtemp()
    out_path = os.path.join(out_dir, f"{base}.{output_ext}")

    if output_ext == "pdf":
        return _images_to_pdf(extract_dir, out_path)
    if output_ext in ("cbz", "zip"):
        _pack_zip(extract_dir, out_path)
    elif output_ext == "tar.gz":
        _pack_tar(extract_dir, out_path, "gz")
    elif output_ext == "tar.bz2":
        _pack_tar(extract_dir, out_path, "bz2")
    elif output_ext == "7z":
        _pack_7z(extract_dir, out_path)
    else:
        raise ValueError(f"Unsupported output: {output_ext}")

    return out_path


def _images_to_pdf(extract_dir: str, out_path: str) -> str:
    paths = [p for p in Path(extract_dir).rglob("*") if p.suffix.lower() in _IMAGE_EXTS]
    if not paths:
        raise ValueError("No images found in archive")
    paths.sort(key=lambda p: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)])
    imgs = [Image.open(str(p)).convert("RGB") for p in paths]
    imgs[0].save(out_path, save_all=True, append_images=imgs[1:])
    return out_path


def _pack_zip(src_dir: str, out_path: str) -> None:
    r = subprocess.run(["zip", "-r", out_path, "."], capture_output=True, cwd=src_dir)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode())


def _pack_tar(src_dir: str, out_path: str, compression: str) -> None:
    flag = "z" if compression == "gz" else "j"
    r = subprocess.run(["tar", f"-c{flag}f", out_path, "-C", src_dir, "."], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode())


def _pack_7z(src_dir: str, out_path: str) -> None:
    r = subprocess.run([_7Z, "a", out_path, "."], capture_output=True, cwd=src_dir)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode())


def _base_name(path: str) -> str:
    name = os.path.basename(path)
    for compound in (".tar.gz", ".tar.bz2", ".tar.xz"):
        if name.lower().endswith(compound):
            return name[: -len(compound)]
    return os.path.splitext(name)[0]
