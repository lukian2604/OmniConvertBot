import os
from .image import convert as convert_image, get_supported_formats as image_formats
from .audio import convert as convert_audio, get_supported_formats as audio_formats
from .video import convert as convert_video, get_supported_formats as video_formats
from .document import convert as convert_document, get_supported_formats as document_formats
from .ebook import convert as convert_ebook, get_supported_formats as ebook_formats
from .archive import convert as convert_archive, get_supported_formats as archive_formats

IMAGE_EXTS    = {"png", "jpg", "jpeg", "webp", "bmp", "gif", "tiff", "ico", "heic", "svg"}
AUDIO_EXTS    = {"mp3", "flac", "ogg", "wav", "m4a", "aac", "wma", "opus"}
VIDEO_EXTS    = {"mp4", "avi", "mov", "webm", "mkv", "flv", "wmv", "mpeg", "3gp"}
DOCUMENT_EXTS = {"docx", "xlsx", "pptx", "txt", "pdf", "html", "odt", "csv", "rtf"}
EBOOK_EXTS    = {"epub", "mobi", "azw3", "fb2"}
ARCHIVE_EXTS  = {"zip", "rar", "7z", "tar.gz", "tar.bz2", "cbr", "cbz", "cb7"}

_COMPOUND_EXTS = (".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst")


def get_ext(filename: str) -> str:
    name = filename.lower()
    for ext in _COMPOUND_EXTS:
        if name.endswith(ext):
            return ext.lstrip(".")
    return os.path.splitext(name)[1].lstrip(".")


def strip_ext(filename: str) -> str:
    name_lower = filename.lower()
    for ext in _COMPOUND_EXTS:
        if name_lower.endswith(ext):
            return filename[: -len(ext)]
    return os.path.splitext(filename)[0]


def detect_category(ext: str) -> str | None:
    ext = ext.lower().lstrip(".")
    if ext in IMAGE_EXTS:
        return "image"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in DOCUMENT_EXTS:
        return "document"
    if ext in EBOOK_EXTS:
        return "ebook"
    if ext in ARCHIVE_EXTS:
        return "archive"
    return None


def get_formats(ext: str) -> list[str]:
    category = detect_category(ext)
    if category == "image":
        return image_formats(ext)
    if category == "audio":
        return audio_formats(ext)
    if category == "video":
        return video_formats(ext)
    if category == "document":
        return document_formats(ext)
    if category == "ebook":
        return ebook_formats(ext)
    if category == "archive":
        return archive_formats(ext)
    return []


def convert(input_path: str, output_ext: str) -> str:
    src_ext = get_ext(os.path.basename(input_path))
    category = detect_category(src_ext)
    if category == "image":
        return convert_image(input_path, output_ext)
    if category == "audio":
        return convert_audio(input_path, output_ext)
    if category == "video":
        return convert_video(input_path, output_ext)
    if category == "document":
        return convert_document(input_path, output_ext)
    if category == "ebook":
        return convert_ebook(input_path, output_ext)
    if category == "archive":
        return convert_archive(input_path, output_ext)
    raise ValueError(f"Unsupported format: {src_ext}")
