# OmniConvertBot — File Converter for Telegram

🔗 Bot: [@lukianDev_bot](https://t.me/lukianDev_bot)

OmniConvertBot is a Telegram bot that converts files across all popular formats — images, audio, video, documents, ebooks, and archives — with no registration required. The interface is fully localised in 8 languages and works entirely through Telegram's native inline keyboard UI.

All conversions happen inside the container using open-source system tools (ffmpeg, LibreOffice, Calibre). The codebase is structured around one converter module per category, each isolated and independently maintainable.

---

## How It Works

1. Send any supported file to the bot
2. The bot detects the format and shows the available output formats as inline buttons
3. Tap a format — the bot converts and sends the file back

File size limits follow Telegram's bot constraints: 20 MB maximum for incoming files, 50 MB for outgoing.

---

## Supported Formats

| Category | Formats |
|---|---|
| Images | png, jpg, jpeg, webp, bmp, gif, tiff, ico, heic, svg |
| Audio | mp3, flac, ogg, wav, m4a, aac, wma, opus |
| Video | mp4, avi, mov, webm, mkv, flv, wmv, mpeg, 3gp |
| Documents | docx, xlsx, pptx, txt, pdf, html, odt, csv, rtf |
| Ebooks | epub, mobi, azw3, fb2 |
| Archives | zip, rar, 7z, tar.gz, tar.bz2, cbr, cbz, cb7 |

---

## Languages

🇬🇧 English · 🇷🇺 Русский · 🇮🇹 Italiano · 🇷🇴 Română · 🇵🇹 Português · 🇸🇦 العربية · 🇯🇵 日本語 · 🇨🇳 中文

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Bot framework | python-telegram-bot 21.6 |
| Image conversion | Pillow 10.4 |
| Audio & video | ffmpeg |
| Documents | LibreOffice headless · pdftotext |
| Ebooks | Calibre ebook-convert |
| Archives | unar · zip · tar · p7zip |
| Deploy | Docker · Railway |

---

## Converters

| Module | Responsibility |
|---|---|
| `image.py` | Raster format conversion via Pillow — handles RGBA→RGB flattening for JPEG output |
| `audio.py` | Format transcoding via ffmpeg |
| `video.py` | Container remuxing, GIF export with palette generation, audio stream extraction |
| `document.py` | Office document conversion via LibreOffice headless · PDF→TXT via pdftotext |
| `ebook.py` | Ebook format conversion via Calibre |
| `archive.py` | Extract with unar, repack to zip/tar.gz/tar.bz2/7z · CBR/CBZ/CB7 to PDF |

---

## Project Structure

```
OmniConvertBot/
├── main.py                   # entry point — registers all handlers and starts polling
├── Dockerfile
├── requirements.txt
│
└── bot/
    ├── handlers/
    │   ├── start.py          # /start → language selection keyboard
    │   ├── file_handler.py   # receives file → validates size → shows format buttons
    │   └── callbacks.py      # button press → download → convert → reply
    │
    ├── converters/
    │   ├── __init__.py       # dispatcher: get_ext, strip_ext, get_formats, convert
    │   ├── image.py
    │   ├── audio.py
    │   ├── video.py
    │   ├── document.py
    │   ├── ebook.py
    │   └── archive.py
    │
    └── locales/
        └── messages.py       # all UI strings in 8 languages
```
