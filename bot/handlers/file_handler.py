import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.locales.messages import LANGUAGES, get
from bot.converters import get_formats, get_ext

_MAX_INPUT_BYTES = 20 * 1024 * 1024  # 20 MB — Telegram bot download limit

_LANG_BY_LABEL = {v: k for k, v in LANGUAGES.items()}


def _user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if text in _LANG_BY_LABEL:
        lang = _LANG_BY_LABEL[text]
        context.user_data["lang"] = lang
        await update.message.reply_text(get(lang, "welcome"))
        return

    lang = _user_lang(context)
    await update.message.reply_text(get(lang, "text_error"))


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lang = _user_lang(context)
    msg = update.message

    tg_file, file_name = _extract_file(msg)
    if tg_file is None:
        await msg.reply_text(get(lang, "format_error"))
        return

    file_size = getattr(tg_file, "file_size", None)
    if file_size and file_size > _MAX_INPUT_BYTES:
        await msg.reply_text(get(lang, "file_too_large"))
        return

    ext = get_ext(file_name)
    formats = get_formats(ext)

    if not formats:
        await msg.reply_text(get(lang, "format_error"))
        return

    buttons = [
        InlineKeyboardButton(f".{fmt}", callback_data=f"convert:{fmt}")
        for fmt in formats
    ]
    rows = [buttons[i:i+4] for i in range(0, len(buttons), 4)]
    reply = await msg.reply_text(
        f"📂 `{file_name}`\n\n{get(lang, 'pick_format')}",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown",
    )

    context.user_data.setdefault("pending_files", {})[reply.message_id] = {
        "file_id": tg_file.file_id,
        "file_name": file_name,
    }


def _extract_file(msg):
    if msg.document:
        return msg.document, msg.document.file_name
    if msg.photo:
        photo = msg.photo[-1]
        return photo, "photo.jpg"
    if msg.audio:
        return msg.audio, msg.audio.file_name or "audio.mp3"
    if msg.video:
        return msg.video, msg.video.file_name or "video.mp4"
    if msg.voice:
        return msg.voice, "voice.ogg"
    if msg.video_note:
        return msg.video_note, "videonote.mp4"
    return None, None
