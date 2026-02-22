import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from SafoneAPI import SafoneAPI

# ===== CONFIG =====
BOT_TOKEN = "8287015753:AAGoGYF_u6-OqfrqGF1_xPY8yIW5FiD9MtE"

# ===== Logging =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== Initialize API =====
api = SafoneAPI()

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Testing Safone chatgpt() endpoint...")

# ===== Handle Messages =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User: {user_message}")

    try:
        # Try calling chatgpt with keyword argument
        response = await api.chatgpt(query=user_message)

        logger.info(f"RAW RESPONSE: {response}")

        if isinstance(response, dict) and response.get("success"):
            reply = response.get("response")
        else:
            reply = str(response)

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"ERROR: {e}")
        await update.message.reply_text(str(e))

# ===== Main =====
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
