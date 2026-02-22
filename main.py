import logging
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"

# Local API (same VPS)
API_URL = "http://127.0.0.1:5500"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("GPT4 Web API Bot Ready.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(API_URL, params={"text": user_message})

        reply = response.text.strip()

        # Telegram max message length safety
        if len(reply) > 4000:
            reply = reply[:4000]

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"API ERROR: {e}")
        await update.message.reply_text("AI server error.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
