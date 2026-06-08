import asyncio
import logging
import os
import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from bot.locales.messages import get
from bot.converters import convert, strip_ext

logger = logging.getLogger(__name__)

_MAX_OUTPUT_BYTES = 50 * 1024 * 1024


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "en")
    data = query.data

    if not data.startswith("convert:"):
        return

    output_ext = data.split(":", 1)[1]
    msg_id = query.message.message_id
    pending = context.user_data.get("pending_files", {}).pop(msg_id, None)

    if not pending:
        await query.edit_message_text(get(lang, "format_error"))
        return

    file_id = pending["file_id"]
    file_name = pending["file_name"]

    await query.edit_message_text(get(lang, "converting"))

    input_path = None
    output_path = None
    try:
        tg_file = await context.bot.get_file(file_id)
        tmp_dir = tempfile.mkdtemp()
        input_path = os.path.join(tmp_dir, file_name)
        await tg_file.download_to_drive(input_path)

        output_path = await asyncio.to_thread(convert, input_path, output_ext)

        if os.path.getsize(output_path) > _MAX_OUTPUT_BYTES:
            await query.message.reply_text(get(lang, "result_too_large"))
            return

        with open(output_path, "rb") as f:
            actual_ext = os.path.splitext(output_path)[1].lstrip(".")
            out_name = strip_ext(file_name) + "." + actual_ext
            await query.message.reply_document(document=f, filename=out_name)

        await query.message.reply_text(get(lang, "done"))

    except Exception as exc:
        logger.exception("Conversion failed: file=%s target=%s error=%s", file_name, output_ext, exc)
        await query.message.reply_text(get(lang, "format_error"))
    finally:
        _cleanup(input_path)
        _cleanup(output_path)


def _cleanup(path: str | None) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
