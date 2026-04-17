from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
import hashlib
import hmac
from urllib.parse import parse_qsl

from django.conf import settings


def check_telegram_auth(init_data: str):
    if not init_data:
        return False  # 🔥 защита

    data = dict(parse_qsl(init_data))

    hash_received = data.pop("hash", None)
    if not hash_received:
        return False

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    secret_key = hashlib.sha256(
        settings.TELEGRAM_BOT_TOKEN.encode()
    ).digest()

    hmac_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(hmac_hash, hash_received)

async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Открыть меню", web_app=WebAppInfo(url="https://yourdomain.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Открыть меню:", reply_markup=reply_markup)

app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()