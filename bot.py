import pytz
import apscheduler.util

def patched_astimezone(tz=None):
    if tz is None:
        return pytz.timezone('Europe/Vienna')
    return tz

apscheduler.util.astimezone = patched_astimezone

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

print(f"TELEGRAM_TOKEN = {TELEGRAM_TOKEN}")
if not TELEGRAM_TOKEN:
    print("Ошибка: TELEGRAM_TOKEN не найден в .env")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton(
                "Открыть Web App",
                web_app=WebAppInfo(url="https://your-webapp-url.com")
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Открой интерфейс:", reply_markup=reply_markup)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Бот запущен...")
    app.run_polling()
