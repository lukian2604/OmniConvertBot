import os
import tempfile
from PIL import Image

_FORMATS: dict[str, list[str]] = {
    "png":  ["jpg", "webp", "bmp", "gif", "tiff", "ico"],
    "jpg":  ["png", "webp", "bmp", "gif", "tiff"],
    "jpeg": ["png", "webp", "bmp", "gif", "tiff"],
    "webp": ["png", "jpg", "bmp", "gif"],
    "bmp":  ["png", "jpg", "webp", "gif"],
    "gif":  ["png", "jpg", "webp", "mp4"],
    "tiff": ["png", "jpg", "webp", "bmp"],
    "ico":  ["png", "jpg"],
    "heic": ["png", "jpg", "webp"],
    "svg":  ["png"],
}

_PIL_FORMAT = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "bmp": "BMP",
    "gif": "GIF",
    "tiff": "TIFF",
    "ico": "ICO",
}


def get_supported_formats(ext: str) -> list[str]:
    return _FORMATS.get(ext.lower().lstrip("."), [])


def convert(input_path: str, output_ext: str) -> str:
    output_ext = output_ext.lower().lstrip(".")
    out_path = _tmp_path(input_path, output_ext)

    if output_ext == "svg":
        raise ValueError("Cannot convert TO svg")

    img = Image.open(input_path).convert("RGBA")

    if output_ext in ("jpg", "jpeg"):
        img = img.convert("RGB")

    pil_fmt = _PIL_FORMAT.get(output_ext, output_ext.upper())
    img.save(out_path, format=pil_fmt)
    return out_path


def _tmp_path(src: str, ext: str) -> str:
    base = os.path.splitext(os.path.basename(src))[0]
    tmp = tempfile.mkdtemp()
    return os.path.join(tmp, f"{base}.{ext}")
