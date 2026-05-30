from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.locales.messages import LANGUAGES


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    langs = list(LANGUAGES.values())
    keyboard = [langs[:4], langs[4:]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("🌐", reply_markup=reply_markup)
