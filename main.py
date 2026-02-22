import logging
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def get_ai_response(prompt: str) -> str:
    url = "https://api.safone.vip/chatbot"

    params = {
        "query": prompt
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)

    print("STATUS:", response.status_code)
    print("RAW:", response.text)

    data = response.json()

    if data.get("success"):
        return data.get("response")
    else:
        return str(data)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Safone Direct API Mode")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reply = await get_ai_response(update.message.text)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(str(e))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
