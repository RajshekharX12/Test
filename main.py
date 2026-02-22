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

# Direct Safone API call
async def get_ai_response(prompt: str) -> str:
    url = "http://api.safone.vip/chatbot"

    params = {
        "query": prompt,
        "user_id": "telegram_user"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, params=params)

    data = response.json()

    if data.get("success"):
        return data.get("response")
    else:
        return "AI failed to respond."

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your AI assistant powered by Safone API."
    )

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User: {user_message}")

    try:
        reply = await get_ai_response(user_message)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("AI error occurred.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
