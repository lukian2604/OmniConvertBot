import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot.handlers.start import start
from bot.handlers.file_handler import handle_text, handle_file
from bot.handlers.callbacks import handle_callback

load_dotenv()


def main() -> None:
    token = os.environ["BOT_TOKEN"]
    app = (
        ApplicationBuilder()
        .token(token)
        .concurrent_updates(True)
        .read_timeout(60)
        .write_timeout(120)
        .connect_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern=r"^convert:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.AUDIO |
        filters.VIDEO | filters.VOICE | filters.VIDEO_NOTE,
        handle_file,
    ))

    print("OmniConvertBot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
